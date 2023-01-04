import os
import pandas as pd
import numpy as np
import ast
import json
import user_widgets
import transform_coord

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

    # If the database does not have columns for GS annotations, create them
    for label in labels:
        if label + '_gs' not in df.columns.to_list():
            df[label+'_gs']= None

    # Read the metadata
    json_files = []
    [json_files.append(file) for file in os.listdir(folder) if file.endswith('.json')]
    
    if not json_files:
        raise OSError('Metadata file missing')
    elif len(find_csv)>1:
        print('Several metadata files on the folder. Using: {}'.format(json_files[0]))

    with open(os.path.join(folder, json_files[0])) as f:
        metadata = json.load(f)

    return df, metadata

def read_annotations(frame_number, labels, df, cropping_coordinates, reduction_factor, image_position):
    '''
    :param frame_number: Number of the frame to read annotations
    :param labels: which labels should we return
    :param df: dataframe to read the labels from
    :param cropping_coordinates: [y0, y1, x1, x2] pixels cropped from original image
    :param reduction_factor: factor used to reduce the image (both x and y dimensions)
    :param image_position: (x,y) traslation of the image in pixels in each dimension
    :return: dictionary containing two keys
        "gs_annotations": dictionary containing gs annotations for each requested label
        "ai_predictions": dictionary containing ai predictions for each requested label
    '''

    annotations_output = {'gs_annotations':{},
                          'ai_predictions':{}
                          }
    

    for lab in labels:
        # If it is for polyp, the format is different because it contains coordinates
        # with the following format [(1, (x,y,width,height)), (2, (x,y,width,height))]
        if lab == 'polyp':
            # ANNOTATIONS
            polyp_gs = df.loc[df['frame'] == str(frame_number)]['polyp_gs'].values
            if polyp_gs:
                if type(polyp_gs[0])==list:
                    # Transform the coordinates to match the resolution of the pqp program
                    rescaled_coordinates = transform_coord.original2pqp(polyp_gs[0], cropping_coordinates, reduction_factor, image_position)
                    annotations_output['gs_annotations']['polyp'] = rescaled_coordinates
                else:
                    print('In read_data, the type of coordinates is not a list anymore')
                    polyp_gs = ast.literal_eval(polyp_gs[0])
                    annotations_output['gs_annotations']['polyp'] = polyp_gs

            #PREDICTIONS
            polyp_ai = df.loc[df['frame'] == str(frame_number)]['{}'.format('polyp')].values
            if polyp_ai == 1:
                annotations_output['ai_predictions']['polyp'] = polyp_ai[0]

        else:
            l_gs = df.loc[df['frame'] == str(frame_number)]['{}_gs'.format(lab)].values[0]
            l_ai = df.loc[df['frame'] == str(frame_number)]['{}'.format(lab)].values[0]
            if l_gs == 1 or l_gs == 2:
                annotations_output['gs_annotations'][lab] = l_gs
            if l_ai == 1 or l_ai == 2:
                annotations_output['ai_predictions'][lab] = l_ai

    
    return annotations_output


def image_attributes(original_resolution):
    '''
    Read the config file for the scale by height factor
    and the image positioning in x and y
    and return the width and height of the image when scaled
    the factor by which the image was reduced
    :param original_resolution: (PIX_in_x, PIX_in_y)
    :return output: {'width_scaled', 'height_scaled', 
                    'reduction_factor', 'position_x',
                    'position_y'}
    '''

    # Read scaling parameter
    out_config = user_widgets.read_config('scale_image_by_height')

    if out_config:
        try:
            scale_image_by_height = int(out_config.split('=')[1])
            # Check that the scale_image_by_height is in the scale
            if not 899 < scale_image_by_height < 1001:
                raise ValueError('scale_image_by_height value must be between 900 and 1000')
        except:
            raise ValueError('scale_image_by_height must contain an integer value')
    else:
        raise OSError('scale_image_by_height value missing in the config')

    factor = scale_image_by_height/original_resolution[1]

    # Read image position
    out_pos_x = user_widgets.read_config('position_x')
    out_pos_y = user_widgets.read_config('position_y')

    if out_pos_x and out_pos_y:
        try:
            position_x = int(out_pos_x.split('=')[1])
            position_y = int(out_pos_y.split('=')[1])
            if not (0<=position_x<=100 and 0<=position_y<=50):
                raise ValueError('Image position values out of the allowed range. Check config.')
        except:
            raise ValueError('Image position values need to be integers')
    else:
        raise OSError('position_x or position_y values are missing in the config file')

    output = {'width_scaled': int(factor*original_resolution[0]),
              'height_scaled': scale_image_by_height,
              'reduction_factor': factor,
              'position_x':position_x,
              'position_y':position_y
              }

    return output

        