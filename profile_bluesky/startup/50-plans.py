print(__file__)

"""plans"""


def frame_set(det, frame_type=0, num_frames=1):
    yield from bps.mv(det.cam.frame_type, frame_type)
    for frame_num in range(num_frames):
        yield from bps.mv(det.cam.acquire, 1)
        while det.cam.acquire.value != 0:
            yield from bps.sleep(0.01)


def series(det, num_images=4, num_darks=3, num_flats=2):
    num_frames = [num_images, num_darks, num_flats]
    total = sum(num_frames)
    print("total frames:", total)

    print("setup")
    yield from bps.mv(
        det.hdf1.num_capture, total,
        det.hdf1.file_write_mode, 'Capture',
        det.cam.image_mode, "Multiple",
    )
    yield from bps.abs_set(
        det.hdf1.capture, 1,
    )

    for i, num in enumerate(num_frames):
        print("type {}, frames {}".format(i, num))
        yield from frame_set(det, frame_type=i, num_frames=num)

    print("restore")
    yield from bps.mv(
        det.hdf1.num_capture, 1,
        det.hdf1.file_write_mode, 'Single',
        det.cam.image_mode, "Single",
        det.cam.num_exposures, 1,
        det.cam.frame_type, 0,
    )


def darks_flats_images(det, shutter, stage, pos_in, pos_out, n_darks=3, n_flats=4, n_images=5, count_time=0.2, md=None):
    """
    (demo only) take a sequence of area detector frames and store them all in one file
    
    dark frames are stored into one dataset
    flat frames are stored into another dataset
    image frames are stored into a third dataset
    
    The area detector HDF5 file plugin has a feature that diverts the image stream
    based on a specific global variable defined in the layout file.
    """
    det.cam.stage_sigs["acquire_time"] = count_time

    yield from bps.mv(
        shutter, "close", 
        det.cam.frame_type, 1,   # Background
        det.hdf1.num_capture, n_darks + n_flats + n_images,
        )
    yield from bp.count([det], num=n_darks, md=md)

    yield from bps.mv(
        shutter, "open", 
        stage, pos_out,
        det.cam.frame_type, 2)   # FlatField
    yield from bp.count([det], num=n_flats, md=md)

    yield from bps.mv(
        shutter, "open", 
        stage, pos_in,
        det.cam.frame_type, 0)   # images
    yield from bp.count([det], num=n_images, md=md)

    yield from bps.mv(shutter, "close")
