Manifest（清单/描述文件）是**基于HTTP的自适应流媒体协议（如HLS和DASH）的核心组件**。它本质上是一个**元数据文件**，告诉播放器如何获取和解码媒体内容。理解其包含的元数据对于流媒体传输至关重要。

以下是Manifest文件中包含的关键元数据及其作用：

---

## **核心作用**
1. **导航地图：** 指引播放器找到媒体片段（Segment）。
2. **内容目录：** 描述媒体内容的结构、可用版本和特性。
3. **播放控制：** 提供播放顺序、时间信息、切换点等规则。
4. **自适应决策依据：** 提供不同码率版本的信息，供播放器根据网络和设备选择。

---

## **HLS (HTTP Live Streaming) Manifest (.m3u8) 元数据详解**
HLS的Manifest是一个文本文件，使用**M3U8格式**（基于M3U播放列表的扩展）。其元数据主要通过**标签**来组织。

### **关键元数据标签与含义**
1. **基础信息与版本：**
    - `#EXTM3U`: 文件头，表明这是一个M3U8文件。
    - `#EXT-X-VERSION: <n>`: 指定HLS协议版本（如3, 4, 5, 6, 7），不同版本支持不同特性（如低延迟、分片类型）。**播放器兼容性关键！**
2. **流媒体类型：**
    - `#EXT-X-PLAYLIST-TYPE: EVENT/VOD`: 标识播放列表类型。
        * `EVENT`: 直播流，列表会动态更新（新片段追加，旧片段可能移除）。播放器通常不能随意跳转。
        * `VOD`: 点播流，列表固定不变，包含所有片段。支持快进快退。
3. **目标时长与序列：**
    - `#EXT-X-TARGETDURATION: <s>`: 指定**每个媒体片段的最大可能持续时间（秒）**。播放器据此准备缓冲区。**必须存在！**
    - `#EXT-X-MEDIA-SEQUENCE: <n>`: (直播) 指定列表中**第一个媒体片段的序列号**。随着直播推进，序列号递增，旧片段被移除时此值增加。
    - `#EXT-X-DISCONTINUITY-SEQUENCE: <n>`: 标识不连续序列的起始点（用于时间线对齐）。
4. **独立媒体片段：**
    - `#EXTINF: <duration>[, <title>]`: **最重要的标签之一**。标记下一个`.ts`或`.m4s`片段的**持续时间（秒）** 和可选的标题。
    - `https://.../segment1.ts`: 紧随`#EXTINF`之后的**实际媒体片段URL**。
5. **多码率自适应 (Master Playlist)：**
    - `#EXT-X-STREAM-INF:`: 定义一个可变码率流的属性。属性包含：
        * `BANDWIDTH=<n>`: **平均比特率（bps）**。播放器选择的主要依据。
        * `AVERAGE-BANDWIDTH=<n>`: 更精确的平均比特率（可选）。
        * `CODECS="<codec_string>"`: 所需的视频/音频编解码器（如`avc1.640028, mp4a.40.2`）。
        * `RESOLUTION=<W>x<H>`: 视频分辨率（如`1280x720`）。
        * `FRAME-RATE=<fps>`: 视频帧率（如`30.000`）。
        * `AUDIO="<group_id>"`, `VIDEO="<group_id>"`, `SUBTITLES="<group_id>"`: 关联到`#EXT-X-MEDIA`定义的媒体组。
        * `HDCP-LEVEL=TYPE-<x>`: 内容保护要求（如`TYPE-0`表示无要求）。
    - `variant_playlist.m3u8`: 紧随`#EXT-X-STREAM-INF`之后的**对应码率的子播放列表URL**。
6. **多语言/字幕/音轨 (Master Playlist)：**
    - `#EXT-X-MEDIA:`: 定义备选的媒体渲染（如不同语言的音频轨、不同语言的字幕轨）。
        * `TYPE=AUDIO/SUBTITLES/CLOSED-CAPTIONS`: 媒体类型。
        * `GROUP-ID="<id>"`: 关联组ID，被`#EXT-X-STREAM-INF`引用。
        * `LANGUAGE="<lang>"`: 语言（如`en`, `zh`）。
        * `NAME="<name>"`: 用户可见的名称（如`English`, `中文`）。
        * `AUTOSELECT=YES/NO`: 是否可自动选择（基于系统语言）。
        * `DEFAULT=YES/NO`: 是否是默认选择。
        * `URI="<media_playlist.m3u8>"`: (仅`TYPE=AUDIO`) 该音轨的子播放列表URL（独立音轨时）。`SUBTITLES`通常内嵌在视频流或WebVTT文件中。
7. **加密与DRM：**
    - `#EXT-X-KEY`: 定义如何解密后续的媒体片段。
        * `METHOD=AES-128/NONE/SAMPLE-AES`: 加密方法。`AES-128`最常用。
        * `URI="<key_url>"`: 获取解密密钥的URL（通常是`.key`文件）。
        * `IV=<hex>`: 初始化向量（可选，系统可生成）。
        * `KEYFORMAT="<format>"`, `KEYFORMATVERSIONS="<versions>"`: 密钥系统格式（如`com.apple.streamingkeydelivery`用于FairPlay）。
    - _(通常与DRM许可证服务器配合使用，如Widevine, FairPlay, PlayReady)_
8. **低延迟HLS (LL-HLS) 扩展：**
    - `#EXT-X-SERVER-CONTROL`: 服务器控制播放列表更新行为（如`CAN-BLOCK-RELOAD=YES`）。
    - `#EXT-X-PART-INF: PART-TARGET=<duration>`: 定义部分片段的目标时长。
    - `#EXT-X-PART`: 定义部分片段（小于完整片段）的URL和时长，用于极低延迟。
    - `#EXT-X-PRELOAD-HINT`: 提示播放器预加载资源（如初始化段、部分片段）。
    - `#EXT-X-RENDITION-REPORT`: 报告其他码率版本的可用片段信息，帮助快速切换。
9. **其他重要标签：**
    - `#EXT-X-DISCONTINUITY`: 标记此后的片段在编码参数、时间戳或连续性上发生突变（如插入广告、切换源）。播放器需要重置解码器。
    - `#EXT-X-I-FRAMES-ONLY`: 表示播放列表只包含I帧（用于快速拖动预览）。
    - `#EXT-X-MAP:`: 指定初始化段`(Initialization Segment)`的URL（用于`fMP4`封装）。提供解码全局信息。
    - `#EXT-X-ENDLIST`: **标记播放列表结束，不再更新**（点播或直播结束）。直播中无此标签表示列表会持续更新。

---

## **MPEG-DASH Manifest (.mpd) 元数据详解**
DASH的Manifest是一个**XML文件**，结构更复杂、标准化程度更高，支持更细粒度的控制。

### **关键XML元素与属性**
1. **根元素与基础信息：**
    - `<MPD>`: 根元素。
        * `xmlns`: 命名空间（如`urn:mpeg:dash:schema:mpd:2011`）。
        * `profiles`: 使用的DASH配置文件（如`urn:mpeg:dash:profile:isoff-live:2011`）。
        * `type="static/dynamic"`: 点播/直播。
        * `availabilityStartTime`: (直播) 表示内容开始可用的绝对时间。
        * `publishTime`: (直播) MPD最后发布时间。
        * `mediaPresentationDuration`: (点播) 整个内容的持续时间。
        * `minBufferTime`: 播放器需要的最小缓冲时间（如`PT1.5S`）。
2. **时间段：**
    - `<Period>`: 将内容划分为逻辑时间段（如正片、广告插播）。每个Period包含一组`AdaptationSet`。
3. **自适应集：**
    - `<AdaptationSet>`: 代表一组可互换的媒体内容（如所有视频轨、所有英文音频轨）。属性：
        * `mimeType`: 媒体类型（如`video/mp4`, `audio/mp4`）。
        * `contentType`: 更细粒度类型（如`video`）。
        * `lang`: 语言（音频/字幕）。
        * `segmentAlignment="true"`: 确保不同Representation的片段边界对齐（方便切换）。
4. **表示形式：**
    - `<Representation>`: **定义一种特定的媒体流（码率版本）**。是自适应选择的基本单位。属性：
        * `id`: 唯一标识符。
        * `bandwidth`: **比特率（bps）**。主要选择依据。
        * `codecs`: 编解码器字符串（如`avc1.640028`）。
        * `width/height`: 视频分辨率。
        * `frameRate`: 视频帧率。
        * `audioSamplingRate`: 音频采样率。
        * `startWithSAP="1"`: 片段以关键帧开始（方便切换）。
5. **片段信息：**
    - **分段模板 (常用)：** `<SegmentTemplate>` 定义片段URL的模式。
        * `media="$RepresentationID$/$Number$.m4s"`: URL模板，变量会被替换。
        * `initialization="$RepresentationID$/init.mp4"`: 初始化段URL。
        * `duration`: 片段时长（媒体时间单位）。
        * `timescale`: 时间单位（如`1`=秒，`90000`=90kHz时钟）。
        * `startNumber`: 第一个片段的序号。
    - **分段列表：** `<SegmentList>` 显式列出每个片段的URL和时长（较少用）。
    - **分段基准：** `<SegmentBase>` 用于单文件点播（较少用）。
    - **低延迟：** `<ServiceDescription>`, `<ProducerReferenceTime>`等元素支持低延迟模式。
6. **内容保护 (DRM)：**
    - `<ContentProtection>`: 定义DRM方案。
        * `schemeIdUri`: 标识DRM系统（如`urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed` 代表Widevine）。
        * `value`: 可选描述。
        * 子元素`<cenc:pssh>`: 包含DRM系统所需的初始化数据（PSSH盒）。
        * 通常配合`<AdaptationSet>`或`<Representation>`使用。
7. **辅助媒体：**
    - 字幕：`<AdaptationSet contentType="text">` + `<Representation>`，通常指向WebVTT文件。
    - 封面图：类似处理。

---

## **总结：Manifest元数据的核心价值**
1. **自适应决策引擎：** `BANDWIDTH`, `CODECS`, `RESOLUTION`等元数据是播放器智能切换码率的基础。
2. **内容组织蓝图：** 清晰定义了媒体流（音/视/字）、多语言/多码率版本、时间段（广告）的结构。
3. **播放导航器：** 精确的片段`URL`、`时长`、`序列号`、`时间戳`确保播放器能按正确顺序和时间获取内容。
4. **安全网关：** `#EXT-X-KEY` (HLS) / `<ContentProtection>` (DASH) 提供DRM集成点，保护内容安全。
5. **低延迟基石：** LL-HLS和LL-DASH的扩展元数据（部分片段、预加载提示、服务端控制）是实现秒级延迟的关键。
6. **兼容性声明：** `#EXT-X-VERSION` (HLS) / `profiles` (DASH) 告知播放器所需的协议支持级别。

**简单来说，Manifest文件就是流媒体播放的“说明书”和“导航图”。** 播放器必须成功下载并正确解析其中的元数据，才能流畅、自适应、安全地播放视频内容。理解这些元数据对于调试播放问题、优化流媒体服务和实现高级功能（如DRM、低延迟）至关重要。

