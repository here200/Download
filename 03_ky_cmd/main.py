import ky_cmd

cmds = ky_cmd.read_file('idm_tmp.txt', encoding='UTF-16')
ky_cmd.excute_commands(cmds)
