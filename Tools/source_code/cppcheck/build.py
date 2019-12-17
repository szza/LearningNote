import os 

if not os.path.exists('./checkInfo'):
    os.mkdir('checkInfo')
    os.chdir('./checkInfo')

checkInfoPah = os.path.abspath(os.curdir)
os.system('cd ..')

# 输出静态错误信息
src = './src'
Static_Info_Path = os.path.join(checkInfoPah, 'checkInfo', 'StaticCheckInfo.txt')
os.system('cppcheck -j 4 --quiet src 2>'+Static_Info_Path)

if not os.path.exists('./build'):
    os.mkdir('build')
    os.chdir('./build')
else:
    os.chdir('./build')
    os.system('rm -rf *')
os.system('cmake .. && cmake --build .')
os.chdir('./bin')

# 输出动态错误信息
files = os.listdir(os.curdir)
dynamic_Info_Path = os.path.join(checkInfoPah, 'checkInfo', 'DynamicCheckInfo.txt')
comline = 'valgrind --leak-check=full --log-file=' +dynamic_Info_Path + ' ./'

for f in files:
    os.system(comline + f)



