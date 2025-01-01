import argparse

from src.simulations.aoa_simulations import run_aoa_range
from src.simulations.general_simulations import custom_run, default_run, run_top_n
from src.simulations.velocity_simulations import run_velocity_range

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose the run mode.")
    parser.add_argument(
        "--custom",
        type=str,
        help="Run custom evaluation with specified UUID.",
    )
    parser.add_argument(
        "--topn",
        type=int,
        help="Simulate top-n airfoils.",
    )
    parser.add_argument(
        "--aoa",
        type=str,
        help="Run AoA simulation with specified UUID.",
    )
    parser.add_argument(
        "--velocity",
        type=str,
        help="Run velocity simulation with specified UUID.",
    )

    args = parser.parse_args()

    if args.custom:
        custom_run(uuid=args.custom)
    elif args.topn is not None:
        run_top_n(n=args.topn)
    elif args.aoa:
        # Example fixed values for demo purposes
        print(args.aoa)
        run_aoa_range(
            uuid=args.aoa,
            airspeed_magnitude=100,
            angle_range_deg=(0, 45),
            n_samples=20,
        )
    elif args.velocity:
        run_velocity_range(
            uuid=args.velocity,
            aoa_deg=5,
            velocity_range=(20, 200),
            n_samples=19,
        )
    else:
        default_run()
