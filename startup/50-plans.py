print(__file__)

# Bluesky plans (scans)

if False:       # demo & testing code
    simulate_peak(calc1, m1, profile="lorentzian")
    RE(tune_centroid([noisy], "noisy", m1, -2, 0, 0.00001, 10))
    
    RE(
        tune_centroid(
            [synthetic_pseudovoigt], "synthetic_pseudovoigt", m1, 
            -2, 0, 0.00001, 10
        )
    )
    RE(
        bp.adaptive_scan(
            [synthetic_pseudovoigt], 'synthetic_pseudovoigt', m1, 
            start=-2, stop=0, min_step=0.01, max_step=1, 
            target_delta=500, backstep=True
        )
    )
