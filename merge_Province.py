basic_path = '/Users/oo/Desktop/9.Blog/chinese_administrative_region/'
dir = basic_path + 'County'
os.chdir(dir)
for path, root, files in os.walk(dir):
    file_names = files.copy()
    break
    
parameter_dictionary = {'LAYERS':file_names, 'OUTPUT':'merged_county.shp'}
processing.run('native:mergevectorlayers', parameter_dictionary)
