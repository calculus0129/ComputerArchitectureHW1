import os, sys

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 3:
        print(f"usage: py {sys.argv[0]} filename1 filename2")
        exit(1)
    input_filenames = sys.argv[1:]
    input_filePaths = list(map(lambda input_filename: os.path.join(os.curdir, input_filename), input_filenames))
    ret = True
    for input_filePath in input_filePaths:
        if os.path.exists(input_filePath) == False:
            print(f"No input file {input_filePath} exists. Please check the file name and path.")
            ret = False
    if not ret: exit(1)
    #f_in = open(input_filePath, 'r')
    with open(input_filePaths[0], 'r') as o:
        for i in input_filePaths[1:]:
            r = True
            with open(i) as oi:
                r = o.read() == oi.read()
            if not r:
                print(f'False: {input_filePaths[0]} and {i}')
                ret = False
    print("Overall Comparison: " + str(ret))

