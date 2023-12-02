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
    Nres = ''
    for msg in res:
        if (re.match('[a-f0-9]*.(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)\:', msg[1:-1])):
            Nres += msg[1:-1]
            Nres += '\n'
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
        print('FilePath: ' + os.getcwd() + os.sep + f'lx-music-api-server_{sha}.exe')

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
        print('FilePath: ' + os.getcwd() + os.sep + f'lx-music-api-server_{vername}.exe')

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