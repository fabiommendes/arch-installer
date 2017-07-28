from collections import defaultdict
import os
import sys


valid_prefixes = ['pacman', 'aur', 'pip', 'npm', 'bash']


def read_instructions():
    "Read packages and return a dictionary of {section: packages}"

    with open('packages.txt') as F:
        lines = (line.rstrip('\n') for line in F.readlines())

    return read_lines(lines)


def read_lines(lines):
    "Return a dictionary of {section: packages} from a list of lines."

    # Prepare lines
    lines = (line.strip(' \n\t') for line in lines)
    lines = (line for line in lines if line)

    # Process
    sections = {}
    packages = [] 
    for line in lines:
        if line.startswith('#'):
            section = line.strip('# ')
            sections[section] = packages = []
        else:
            for prefix in valid_prefixes:
                if line.startswith(prefix + '/'):
                    name = line[len(prefix) + 1:]
                    break
            else:
                name = line
                prefix = 'pacman'

            packages.append((prefix, name))

    return sections


def select_installs(packages, sections):
    """
    Return a map of {prefix: packages} for all selected packages of each prefix
    """

    result = defaultdict(list)
    for section, pkg_list in packages.items():
        if section in sections:
            for (prefix, name) in pkg_list:
                result[prefix].append(name)
    return result


def exec_cmd(cmd, prompt=None):
    if prompt is None:
        prompt = globals().get('prompt', True)

    print('cmd: ', cmd)
    print()
    if prompt and input('Run command? [Y/n] ').lower() not in ['y', 'yes', '']:
        print('skipping...\n')
    elif os.system(cmd) != 0:
        raise SystemExit('command returned with an error')


def install_pacman(packages, prompt=None):
    if packages:
        pkgs = ' '.join(packages)
        exec_cmd('sudo pacman -Sy --noconfirm %s' % pkgs, prompt)


def install_aur(packages, prompt=None):
    if packages:
        pkgs = ' '.join(packages)
        exec_cmd('yaourt -Sy --noconfirm %s' % pkgs, prompt)


def install_pip(packages, prompt=None):
    if packages:
        pkgs = ' '.join(packages)
        exec_cmd('sudo pip install %s' % pkgs, prompt)


def install_bash(cmds, prompt=None):
    if cmds:
        cmd = '\n'.join(cmds)
        exec_cmd(cmd, prompt)


def install_npm(packages, prompt=None):
    if packages:
        pkgs = ' '.join(packages)
        exec_cmd('sudo npm install -y %s' % pkgs, prompt)


def main(argv):
    instructions = read_instructions()
    
    global prompt
    prompt = True
    if '--no-prompt' in argv:
        prompt = False
        argv.remove('--no-prompt') 
    
    sections = argv
    
    if not argv:
        print('List of available sections:')
        for section in sorted(instructions.keys()):
            print('  *', section)
    else:
        sections = set(sections)
        if sections == {'all'}:
            sections = set(instructions.keys()) 

        installs = select_installs(instructions, sections)
        for prefix in valid_prefixes:
            if prefix in installs:
                packages = installs[prefix]
                installer = globals()['install_' + prefix]
                installer(packages)


if __name__ == '__main__':
    argv = sys.argv[:]
    if argv[0] == 'install.py':
        del argv[0]
    main(argv)