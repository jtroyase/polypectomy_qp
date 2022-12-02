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

def read_annotations(frame_number, labels, df):
    '''
    :param frame_number: Number of the frame to read annotations
    :param labels: which labels should we return
    :param df: dataframe to read the labels from
    :return: dictionary containing two keys
        "gs_annotations": dictionary containing gs annotations for each requested label
        "ai_predictions": dictionary containing ai predictions for each requested label
    '''

    annotations_output = {'gs_annotations':[],
                          'ai_predictions':[]
                          }
    
    for lab in labels:
        
        # If it is for polyp, the format is different because it contains coordinates
        # with the following format [(1, (x,y,width,height)), (2, (x,y,width,height))]
        if lab == 'polyp':
            # ANNOTATIONS
            polyp_gs = df.loc[df['frame'] == frame_number]['polyp_gs'].values
            if polyp_gs:
                polyp_gs = ast.literal_eval(polyp_gs[0])
                annotations_output['gs_annotations']['polyp'] = polyp_gs
            #PREDICTIONS
            polyp_ai = df.loc[df['frame'] == frame_number]['{}'.format('polyp')].values
            if polyp_ai:
                annotations_output['ai_predictions']['polyp'] = polyp_ai[0]

        else:
            l_gs = df.loc[df['frame'] == frame_number]['{}_gs'.format(lab)].values
            l_ai = df.loc[df['frame'] == frame_number]['{}'.format(lab)].values
            if l_gs:
                annotations_output['gs_annotations'][lab] = l_gs[0]
            if l_ai:
                annotations_output['ai_predictions'][lab] = l_ai[0]

    return annotations_output