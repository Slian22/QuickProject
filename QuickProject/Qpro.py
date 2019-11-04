import os
import re
import sys

if sys.platform.startswith('win'):
    is_win = True
    dir_char = '\\'
else:
    is_win = False
    dir_char = '/'
work_dir = os.getcwd()
work_project = work_dir.split(dir_char)[-1]
work_dir += dir_char

cpp_template = """#include <iostream>
using namespace std;

int main(int argc, char **argv) {

    return 0;
}
"""

c_template = """#include <stdio.h>

int main(int argc, char **argv) {

    return 0;
}
"""


def main():
    if '-h' in sys.argv:
        print('usage:\n'
              '\t * [Qpro -init   ]: let dir be a Qpro project!\n'
              '\t * [Qpro -h      ]: help\n'
              '\t * [Qpro -update ]: update Qpro\n'
              '\t * [Qpro -adjust ]: adjust configure\n'
              '\t * [Qpro -c name ]: create a Qpro project\n'
              '\t * [tmpm *       ]: manage your template\n'
              '\t * [run *        ]: run your Qpro project\n'
              '\t * [detector -[p/f][p/f] ]: run beat detector for two source files')
        exit(0)
    elif '-update' in sys.argv:
        os.system('pip3 install Qpro --upgrade')
        exit(0)
    elif '-c' in sys.argv:
        try:
            project_name = sys.argv[sys.argv.index('-c') + 1]
        except IndexError:
            exit('usage: Qpro -c project')
        else:
            if os.path.exists(project_name) and os.path.isdir(project_name):
                exit('"%s" is exist!' % (work_dir + project_name + dir_char))
            os.mkdir(project_name)
            is_cpp = True if input('Is a cpp project? [y/n]:') == 'y' else False
            source_file = 'main.cpp' if is_cpp else 'main.c'
            with open(project_name + dir_char + source_file, 'w') as f:
                f.write(cpp_template if is_cpp else c_template)
            os.mkdir(project_name + dir_char + 'dist')
            os.mkdir(project_name + dir_char + 'template')
            info = [
                ['compile_tool', 'g++ -std=c++11' if is_cpp else 'gcc -std=c11', ''],
                ['compile_filename', source_file],
                ['executable_filename', 'dist' + dir_char + project_name],
                ['input_file', 'dist' + dir_char + 'input.txt'],
                ['template_root', 'template' + dir_char]
            ]
            with open(project_name + dir_char + 'project_configure.csv', 'w') as f:
                for row in info:
                    f.write(','.join(row) + '\n')
            with open(project_name + dir_char + info[3][-1], 'w') as f:
                f.write('edit this file to make input')
            with open(project_name + dir_char + info[1][-1], 'r') as f:
                main_cont = f.read()
            with open(project_name + dir_char + 'template' + dir_char + 'main', 'w') as f:
                f.write(main_cont)
    elif '-adjust' in sys.argv:
        config = {}
        try:
            with open('project_configure.csv', 'r') as f:
                for row in f.readlines():
                    row = row.split(',')
                    config[row[0]] = [i.strip() for i in row[1:]]
                for i in config:
                    if i != 'compile_tool':
                        config[i] = config[i][0]
        except IOError:
            exit("No file named: project_configure.csv\n May you need run:\"Qpro -init\" first!")
        import tkinter as tk
        win = tk.Tk()
        win.title('Qpro项目调整器')
        key_to_name = {
            'compile_tool': '编译指令:',
            'compile_filename': '源程序:',
            'executable_filename': '项目地址:',
            'input_file': '输入文件:',
            'template_root': '模板目录:'
        }
        all_dt = {}
        for i, v in enumerate(config):
            tk.Label(win, text='%12s' % key_to_name[v]).grid(row=i, column=0)
            if v == 'compile_tool':
                stringvar1 = tk.Variable()
                stringvar1.set(config[v][0])
                stringvar2 = tk.Variable()
                stringvar2.set(config[v][1])
                tk.Entry(win, textvariable=stringvar1, width=20).grid(row=i, column=1)
                tk.Entry(win, textvariable=stringvar2, width=19).grid(row=i, column=2)
                all_dt[v] = [stringvar1, stringvar2]
            else:
                stringvar1 = tk.Variable()
                stringvar1.set(config[v])
                tk.Entry(win, textvariable=stringvar1, width=40).grid(row=i, column=1, columnspan=2)
                all_dt[v] = stringvar1

        def deal_config():
            for i in all_dt:
                if i == 'compile_tool':
                    config[i] = [all_dt[i][0].get(), all_dt[i][1].get()]
                else:
                    config[i] = all_dt[i].get()
            if not config['template_root'].endswith(dir_char):
                config['template_root'] += dir_char
            win.destroy()
            with open('project_configure.csv', 'w') as file:
                for line in config:
                    if line == 'compile_tool':
                        file.write('%s,%s\n' % (line, ','.join(config[line])))
                    else:
                        file.write('%s,%s\n' % (line, config[line]))

        tk.Button(win, text='确认', command=deal_config, width=10).grid(row=5, column=0, columnspan=3)
        tk.mainloop()
    elif '-init' not in sys.argv:
        exit('wrong usage! Run "Qpro -h" for help!')
    elif not os.path.exists('project_configure.csv'):
        if not os.path.exists('CMakeLists.txt'):
            ask = input('Not an CLion Project!' + 'You need make configure manually [y/n]:').strip()
            if 'y' not in ask and 'Y' not in ask:
                exit(0)
            is_cpp = True if input('Is a cpp project? [y/n]:').strip() == 'y' else False
            source_file = 'main.c' + ('pp' if is_cpp else '')
            while not os.path.exists(source_file):
                source_file = input('Not found "%s", set compile_filename:' % source_file).strip()
            global work_project
            while not work_project:
                work_project = input('You need to set project name:').strip()
            if not os.path.exists('dist') or not os.path.isdir('dist'):
                os.mkdir('dist')
            project_name = 'dist' + dir_char + work_project
        else:
            with open("CMakeLists.txt", 'r') as f:
                content = f.read()
            project_name = re.findall('project\((.*?)\)', content)[0].split()[0]
            if '.cpp' in content or '.CPP' in content:
                is_cpp = True
            else:
                is_cpp = False
            print('Project name:%s(%s)' % (project_name, 'CPP' if is_cpp else 'C'))
            project_name = 'cmake-build-debug' + dir_char + project_name
            source_file = 'main.c' + ('pp' if is_cpp else '')
        pro_root = dir_char.join(project_name.split(dir_char)[:-1])
        default_input = pro_root + dir_char + 'input.txt'
        print('adding project_configure')
        info = [
            ['compile_tool', 'g++ -std=c++11' if is_cpp else 'gcc -std=c11', ''],
            ['compile_filename', source_file],
            ['executable_filename', project_name],
            ['input_file', default_input],
            ['template_root', 'template' + dir_char]
        ]
        with open('project_configure.csv', 'w') as f:
            for row in info:
                f.write(','.join(row) + '\n')
        with open(info[3][-1], 'w') as f:
            f.write('edit this file to make input')
        if not os.path.exists('template') or not os.path.isdir('template'):
            os.mkdir('template')
        with open(info[1][-1], 'r') as f:
            main_cont = f.read()
        with open('template' + dir_char + 'main', 'w') as f:
            f.write(main_cont)
    else:
        exit("You have configured your project, see project_configure to adjust your configure!")


if __name__ == '__main__':
    main()
