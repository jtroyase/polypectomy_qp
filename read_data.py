import os
import pandas as pd
import json
import user_widgets
import transform_coord
import ast

def get_img_paths(dir, dataframe, extensions=('.jpg', '.png', '.jpeg')):
    '''
    :param dir: folder with files
    :param df: pandas database object
    :param extensions: tuple with file endings. e.g. ('.jpg', '.png'). Files with these endings that are included in database will be added to img_paths
    :return: list of all filenames
    '''

    # We use a set for fast lookup
    img_paths = set()

    dir = os.path.join(dir, 'Frames')
    
    for filename in os.listdir(dir):
        if filename.lower().endswith(extensions):
            img_paths.add(os.path.join(dir, filename))


    # Use os.path.join() to construct image path
    dataframe['im_path'] = dataframe['frame'].apply(lambda x: os.path.join(dir, x))

    # Use set data structure to check if the image path is in the img_paths list
    img_annotate_path = dataframe.loc[dataframe['im_path'].isin(img_paths)]['im_path'].tolist()

    # Raise an error if there are any missing images
    missing_imgs = dataframe.loc[~dataframe['im_path'].isin(img_paths)]['im_path'].tolist()

    if missing_imgs:
        raise OSError('Image {} in database that needs to be annotated not found'.format(missing_imgs))

    # Eliminate the column im_path because no longer needed
    dataframe.drop('im_path', axis=1, inplace=True)

    return img_annotate_path


def get_database(folder, labels_to_annotate):
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
    df = pd.read_csv(df_loc)

    # If the database does not have columns for GS annotations, create them
    for label in labels_to_annotate:
        if label + '_gs' not in df.columns.to_list():
            df[label+'_gs']= None

    # If the database does not have column for resection, create it
    if 'resections' not in df.columns.to_list():
        df['resections']=None

    # Create a column with the frame number in integers
    df['frame_integers'] = df['frame'].apply(lambda x: int(x[:-4]))

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

def read_annotations(frame_number, labels_to_annotate, labels_to_plot, df, cropping_coordinates, reduction_factor, image_position):
    '''
    :param frame_number: Number of the frame (integer) to read annotations. E.g. 1569
    :param labels: which labels should we read data from
    :param df: dataframe to read the labels from
    :param cropping_coordinates: [y0, y1, x1, x2] pixels cropped from original image
    :param reduction_factor: factor used to reduce the image (both x and y dimensions)
    :param image_position: (x,y) traslation of the image in pixels in each dimension
    :return: dictionary containing two keys
        "gs_annotations": dictionary containing gs annotations for each requested label
        "ai_predictions": dictionary containing ai predictions for each requested label
        "resections": dictionary containing the point of no returns (resections) for each
                      requested label.
    '''

    annotations_output = {'gs_annotations':{},
                          'ai_predictions':{}
                          }
    
    
    # This is to read the data for labels to annotate
    for lab in labels_to_annotate:
        # If it is for polyp, the format is different because it contains coordinates
        # with the following format [(1, (x,y,width,height)), (2, (x,y,width,height))]
        if lab == 'polyp':
            # ANNOTATIONS
            polyp_gs = df.loc[df['frame_integers'] == frame_number]['polyp_gs'].values

            if polyp_gs:
                if type(polyp_gs[0])==list:
                    # Transform the coordinates to match the resolution of the pqp program
                    rescaled_coordinates = transform_coord.original2pqp(polyp_gs[0], cropping_coordinates, reduction_factor, image_position)
                    annotations_output['gs_annotations']['polyp'] = rescaled_coordinates
                if type(polyp_gs[0])==str:
                    # Transform the coordinates to list
                    coordinates = ast.literal_eval(polyp_gs[0])
                    # Transform the coordinates to match the resolution of the pqp program
                    rescaled_coordinates = transform_coord.original2pqp(coordinates, cropping_coordinates, reduction_factor, image_position)
                    annotations_output['gs_annotations']['polyp'] = rescaled_coordinates
        else:
            l_gs = df.loc[df['frame_integers'] == frame_number]['{}_gs'.format(lab)].values
            if l_gs:
                if l_gs[0] == 1 or l_gs[0] == 2:
                    annotations_output['gs_annotations'][lab] = l_gs[0]


    # This is to read the data for labels to plot
    for lab in labels_to_plot: 
        lab_plot = df.loc[df['frame_integers'] == frame_number]['{}'.format(lab)].values
        if lab_plot and lab_plot[0] == 1:
            annotations_output['ai_predictions'][lab] = lab_plot[0]


    # RESECTION INSTRUMENTS
    # Check that the length of the resection annotation is 1
    frame_resection_annotations = df.loc[df['frame_integers'] == frame_number]['resections'].tolist()
    
    if len(frame_resection_annotations) > 1:
        raise ValueError('Multiple resection annotations in frame: {}'.format(frame_number))
    elif len(frame_resection_annotations) == 0:
        annotations_output['resections'] = None
    else:
        annotations_output['resections'] = frame_resection_annotations[0]
    
    return annotations_output


def image_attributes(original_resolution, file_name):
    '''
    Read the config file for the scale by height factor
    and the image positioning in x and y
    and return the width and height of the image when scaled
    the factor by which the image was reduced
    :param original_resolution: (PIX_in_x, PIX_in_y)
    :param file_name: name of the video that we read
    :return output: {'width_scaled', 'height_scaled', 
                    'reduction_factor', 'position_x',
                    'position_y'}
    '''

    # Read scaling parameter
    out_config = user_widgets.read_config('scale_image_by_height')
    try:
        out_config = ast.literal_eval(out_config.split('=')[1])
        for key in out_config.keys():
            if key in file_name:
                scale_image_by_height = out_config[key]
                break
        if key == 'default':
            scale_image_by_height = out_config['default']
        if key == 'Heil_1' or key == 'Heil_2' or key == 'PassekEndoBox':
            added_panel = 14
        elif key == 'simonis':
            added_panel = 100
            print('here')
        else:
            added_panel = 0
    except:
        print('Scale image by height ast failed. scale_image_by_height = 1000')
        scale_image_by_height = 1000

    
    try:
        scale_image_by_height = int(scale_image_by_height)
        # Check that the scale_image_by_height is in the scale
        if not 899 < scale_image_by_height < 1051:
            print('Scale image by height must be between 900 and 1050. Default = 1000')
            scale_image_by_height = 1000
    except:
        print('scale_image_by_height must contain an integer value. Default = 1000')


    factor = scale_image_by_height/original_resolution[1]

    # Read image position
    out_pos_x = user_widgets.read_config('position_x')
    out_pos_y = user_widgets.read_config('position_y')


    try:
        out_pos_x = ast.literal_eval(" ".join(out_pos_x.split('=')[1].split()))
        out_pos_y = ast.literal_eval(" ".join(out_pos_y.split('=')[1].split()))
        for key in out_pos_x.keys():
            if key in file_name:
                out_pos_x = out_pos_x[key]
                out_pos_y = out_pos_y[key]
                break
        if key == 'default':
            out_pos_x = out_pos_x['default']
            out_pos_y = out_pos_y['default']
    except:
        print('Position x or y ast failed. pos_x=25, pos_y=35')
        out_pos_x = 25
        out_pos_y = 35


    try:
        position_x = int(out_pos_x)
        position_y = int(out_pos_y)
        if not (0<=position_x<=100 and 0<=position_y<=56):
            print('Position x or y of the image not in the range. Change config. Default values implemented')
            position_x = 25
            position_y = 35
    except:
        print('Position x or y must contain an integer value. Default values implemented')

    output = {'width_scaled': int(factor*original_resolution[0]),
              'height_scaled': scale_image_by_height,
              'reduction_factor': factor,
              'position_x':position_x,
              'position_y':position_y,
              'added_panel':added_panel
              }

    return output

        
