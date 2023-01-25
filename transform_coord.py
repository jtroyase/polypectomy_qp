def original2pqp(coordinates, cropping_coordinates, reduction_factor, image_position):
    '''
    Transforms the coordinates coming from the original resolution of the
    video (images) to the coordinates displayed in the pqp.
    :param coordinates: coordinates to transform
    :param cropping_coordinates: [y0, y1, x1, x2] pixels cropped from original
    :param reduction_factor: factor used to reduce the image (both x and y dimensions)
    :param image_position: (x,y) translation of the image in pixels in each dimension
    '''

    rescaled_coordinates = []

    for polyp in coordinates:
        polyp_id = polyp[0]
        coord = polyp[1]

        # Traslate the image to account for the cropping
        x = coord[0] - cropping_coordinates[2]
        y = coord[1] - cropping_coordinates[0]

        # Scale the coordinates to account for the image scaling
        x = int(x*reduction_factor)
        y = int(y*reduction_factor)
        width = int(coord[2]*reduction_factor)
        height = int(coord[3]*reduction_factor)
        
        # Traslate coords according to the position of the image in the screen
        x = x + image_position[0]
        y = y + image_position[1]

        rescaled_coordinates.append((polyp_id, (x,y,width,height)))

    return rescaled_coordinates

def pqp2original(coordinates, cropping_coordinates, reduction_factor, image_position):
    '''
    Transforms the coordinates displayed in the pqp
    to the coming from the original resolution
    of the video(images) to the coordinates displayed in the pqp
    :param coordinates: coordinates to transform
    :param cropping_coordinates: [y0, y1, x1, x2] pixels cropped from original
    :param reduction_factor: factor used to reduce the image (both x and y dimensions)
    :param image_position: (x,y) translation of the image in pixels in each dimension
    '''

    rescaled_coordinates = []

    for polyp in coordinates:
        polyp_id = polyp[0]
        coord = polyp[1]

        # First eliminate the effect of the traslation of the image in pqp
        x = coord[0] - image_position[0]
        y = coord[1] - image_position[1]

        # Increase the resolution to eliminate the effect of image scaling
        x = int(x/reduction_factor)
        y = int(y/reduction_factor)
        width = int(coord[2]/reduction_factor)
        height = int(coord[3]/reduction_factor)

        # Traslate the image to eliminate the effect of cropping
        x = x + cropping_coordinates[2]
        y = y + cropping_coordinates[0]

        rescaled_coordinates.append((polyp_id, (x,y,width,height)))

    return rescaled_coordinates