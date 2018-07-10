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
