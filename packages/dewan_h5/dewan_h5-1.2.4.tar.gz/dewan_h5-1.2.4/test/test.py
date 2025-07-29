from dewan_h5_git.dewan_h5 import DewanH5
from sniffing_dynamics import sniffing
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pandas as pd
from tqdm import tqdm

def main():
    file_path = Path('/mnt/r2d2/11_Data/GoodSniffData/')
    animal_dirs = file_path.iterdir()
    animal_dirs = [item for item in animal_dirs if item.is_dir()]

    num_original_trials = 0
    num_dropped_trials = 0
    num_final_trials = 0

    animal_info = {}


    animal_info = pd.DataFrame(columns=['191', '194', '195', '198', '199', '200'], index=['0.e+00', '1.0e-03', '1.e-04', '1.e-05', '1.e-06', '1.0e-07', '1.e-08', '1.e-09'])

    for animal_dir in tqdm(animal_dirs, total=len(animal_dirs)):
        good_h5_dir = animal_dir.joinpath('good')
        h5_files = list(good_h5_dir.glob('*.h5'))
        for h5_file in tqdm(h5_files, total=len(h5_files)):
            try:
                with DewanH5(h5_file) as h5:

                    mouse = h5.mouse
                    concentration = h5.concentration
                    num_trials = h5.total_trials

                    animal_info.loc[concentration, str(mouse)] = num_trials

                    num_final_trials += h5.total_trials
                    num_dropped_trials += len(h5.early_lick_trials)
                    num_original_trials += h5.num_initial_trials

            except Exception as e:
                print(h5_file)
                print(e)

    print(animal_info)
    print(f'Num Original Trials: {num_original_trials}')
    print(f'Num Dropped Trials: {num_dropped_trials}')
    print(f'Num Final Trials: {num_final_trials}')

def one_file():
    file_path = Path('/mnt/r2d2/11_Data/GoodSniffData/mouse194_sess1_D2025_2_25T12_18_28.h5')
    with DewanH5(file_path, trim_trials=True) as h5:
        for trial in h5.trial_parameters.index:
            sniff_data = h5.sniff[trial].loc[-1000:2000]
            lick_timestamps = h5.lick1[trial]
            lick_timestamps = np.array(lick_timestamps)
            lick_timestamps = lick_timestamps[lick_timestamps <= 2000]
            grace_period_end = h5.trial_parameters['grace_period_ms'].loc[trial]
            grace_period_end = grace_period_end - 50

            plt.plot(sniff_data)
            print(trial)
            plt.vlines(x=lick_timestamps, ymin=min(sniff_data), ymax=max(sniff_data), color='r')
            plt.vlines(x=grace_period_end, ymin=min(sniff_data), ymax=max(sniff_data), color='k')
            plt.show()


if __name__ == '__main__':
    main()
    # one_file()