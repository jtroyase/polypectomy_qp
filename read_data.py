import os
import pandas as pd
import numpy as np

def get_img_paths(dir, df, extensions=('.jpg', '.png', '.jpeg')):
    '''
    :param dir: folder with files
    :param df: pandas database object
    :param extensions: tuple with file endings. e.g. ('.jpg', '.png'). Files with these endings that are included in database will be added to img_paths
    :return: list of all filenames
    '''

    img_paths = []

    dir = os.path.join(dir, 'Frames')
    
    for filename in os.listdir(dir):
        if filename.lower().endswith(extensions):
            img_paths.append(os.path.join(dir, filename))


    img_annotate_path = []
    
    for index, row in df.iterrows():
        frames_df = row['frame']
        while len(frames_df) < 7:
            frames_df = '0' + frames_df

        im_path = os.path.join(dir, frames_df + '.jpg')

        if im_path in img_paths:
            img_annotate_path.append(im_path)
        else:
            raise OSError('Image {} in database that needs to be annotated not found'.format(im_path))

    return img_annotate_path


def get_database(folder, labels):
    '''
    :param selected_folder: Path of the folder of the data to annotate
    :param labels: labels that user has chosen to annotate
    :return: Database as a pandas object
    '''

    # Find database in the provided folder
    find_csv = []
    [find_csv.append(file) for file in os.listdir(folder) if file.endswith('csv')]

    # Raise Errors if file is not found or there are several files
    if not find_csv:
        raise OSError('Database csv file missing')
    elif len(find_csv) > 1:
        print('Several database on the folder. Using: {}'.format(find_csv[0]))
        
    # Read the database
    df_loc = os.path.join(folder, find_csv[0])
    df = pd.read_csv(df_loc, dtype = {'frame':str})

    # If the database does not have columns for HiWi annotations, create them
    for label in labels:
        if label + '_gs' not in df.columns.to_list():
            df[label+'_gs']= np.nan

    return df