import subprocess
import sys
import re
import os


def get_latest_tag():
    return subprocess.check_output(['git', 'describe', '--abbrev=0', '--tags']).decode('utf-8').strip()


def get_changelog():
    res = subprocess.check_output(
        ['git', 'log', f'{get_latest_tag()}..HEAD', '--pretty=format:"%h %s"']).decode('utf-8').strip()
    res = res.split('\n')
    featMsg = []
    fixMsg = []
    docsMsg = []
    buildMsg = []
    otherMsg = []
    noticeMsg = []
    unknownMsg = []
    for msg in res:
        if (re.match('[a-f0-9]*.(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|notice)\:', msg[1:-1])):
            msg = msg[1:-1]
            if msg[8:].startswith('notice:'):
                noticeMsg.append(msg)
            elif msg[8:].startswith('feat:'):
                featMsg.append(msg)
            elif msg[8:].startswith('fix:'):
                fixMsg.append(msg)
            elif msg[8:].startswith('docs:'):
                docsMsg.append(msg)
            elif msg[8:].startswith('build:'):
                buildMsg.append(msg)
            else:
                otherMsg.append(msg)
        else:
            msg = msg[1:-1]
            unknownMsg.append(msg)
    # final
    Nres = ''
    if (len(noticeMsg) > 0):
        Nres += '## 公告\n'
        for msg in noticeMsg:
            Nres += f'- {msg}\n'
    if (len(featMsg) > 0):
        Nres += '## 功能更新\n'
        for msg in featMsg:
            Nres += f'- {msg}\n'
    if (len(fixMsg) > 0):
        Nres += '## bug修复\n'
        for msg in fixMsg:
            Nres += f'- {msg}\n'
    if (len(docsMsg) > 0):
        Nres += '## 文档更新\n'
        for msg in docsMsg:
            Nres += f'- {msg}\n'
    if (len(unknownMsg) > 0):
        Nres += '## 未知类型的提交\n'
        for msg in unknownMsg:
            Nres += f'- {msg}\n'
    if (len(buildMsg) > 0):
        Nres += '## 构建配置\n'
        for msg in buildMsg:
            Nres += f'- {msg}\n'
    if (len(otherMsg) > 0):
        Nres += '## 其他\n'
        for msg in otherMsg:
            Nres += f'- {msg}\n'
    return Nres.strip()


def get_python_path():
    return sys.executable


def get_latest_commit_sha():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()[0:7]


def build_test(fileName):
    os.environ['build'] = 'T'
    try:
        import PyInstaller as UNUSED
    except ModuleNotFoundError:
        print('[ERROR]: Please install PyInstaller module first.',
              'If you have the module installed,',
              'Please check if you forgetting to activate the virtualenv.', sep='\n')
        sys.exit(1)

    sha = get_latest_commit_sha()

    popen = subprocess.Popen([get_python_path(),
                              '-m',
                              'PyInstaller',
                              '-F',
                              '--name',
                              fileName if fileName else f'lx-music-api-server_{sha}',
                              'main.py'])

    print('PyInstaller process started, PID: ' + str(popen.pid))
    print('Please wait for a while...')
    popen.wait()

    if (popen.returncode != 0):
        print(f'[ERROR]: PyInstaller build with code {popen.returncode}.', 
              'Please check the output log,', 
              'this may inculde errors or warnings.', sep='\n')
        sys.exit(popen.returncode)
    else:
        print('[SUCCESS]: PyInstaller build success.')
        print('FilePath: ' + os.getcwd() + os.sep + os.listdir(os.getcwd() + '/dist')[0])

def build_release(fileName = ''):
    os.environ['build'] = 'R'
    try:
        import PyInstaller as UNUSED
    except ModuleNotFoundError:
        print('[ERROR]: Please install PyInstaller module first.',
              'If you have the module installed,',
              'Please check if you forgetting to activate the virtualenv.', sep='\n')
        sys.exit(1)

    vername = get_latest_tag()

    popen = subprocess.Popen([get_python_path(),
                              '-m',
                              'PyInstaller',
                              '-F',
                              '--name',
                              fileName if fileName else f'lx-music-api-server_{vername}',
                              'main.py'])

    print('PyInstaller process started, PID: ' + str(popen.pid))
    print('Please wait for a while...')
    popen.wait()

    if (popen.returncode != 0):
        print(f'[ERROR]: PyInstaller build with code {popen.returncode}.', 
              'Please check the output log,', 
              'this may inculde errors or warnings.', sep='\n')
        sys.exit(popen.returncode)
    else:
        print('[SUCCESS]: PyInstaller build success.')
        print('FilePath: ' + os.getcwd() + os.sep + os.listdir(os.getcwd() + '/dist')[0])

argv = sys.argv

argv.pop(0)

commands = []
options = []

further_info_required_options = ['-f', '--fileName']

for arg in argv:
    if (arg.startswith('-')):
        options.append(arg)
        if (arg in further_info_required_options):
            options.append(argv[argv.index(arg) + 1])
    else:
        if (arg not in options):
            commands.append(arg)

def main():
    fileName = ''
    for o in options:
        if (o == '-f' or o == '--fileName'):
            try:
                fileName = options[options.index(o) + 1]
            except:
                print('[ERROR] No fileName specified')
                sys.exit(1)
        elif (o == '-h' or o == '--help'):
            print('Usage: build.py [options] <command>')
            print('Options:')
            print('  -f, --filename <fileName>  Specify the fileName of the executable.')
            print('  -h, --help                 Show this help message and exit.')
            print('Commands:')
            print('  build test                 Build test executable.')
            print('  build release              Build release executable.')
            print('  changelog                  Show changelog.')
            sys.exit(0)
        elif (o.startswith('-')):
            print(f'[ERROR] Invalid option "{o}" specified.')
            sys.exit(1)
    if (len(commands) == 0):
        print('[ERROR] No command specified')
        sys.exit(0)
    try:
        if (commands[0] == 'build'):
            if (len(commands) == 1):
                print('[WARNING] No build command specified, defaulting to build test.')
                build_test(fileName)
                sys.exit(0)
            elif (commands[1] == 'test'):
                build_test(fileName)
                sys.exit(0)
            elif (commands[1] == 'release'):
                build_release(fileName)
                sys.exit(0)
            else:
                print('[ERROR] Invalid build command specified.')
                sys.exit(1)
        elif (commands[0] == 'changelog'):
            print(get_changelog())
            sys.exit(0)
        else:
            print('[ERROR] Invalid command specified.')
            sys.exit(1)
    except IndexError:
        print('[ERROR] Invalid command specified.')
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('[INFO] Aborting...')
        sys.exit(0)