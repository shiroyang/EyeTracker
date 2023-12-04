import threading
# from OOP_em import EyeTrackerDataCollector
from OOP_image_stimuli import StimuliExperiment

# def run_eye_tracker():
#     collector = EyeTrackerDataCollector()
#     collector.start_collecting()

def run_stimuli_experiment():
    experiment = StimuliExperiment()
    experiment.run()

if __name__ == "__main__":
    # Create threads
    #thread_eye = threading.Thread(target=run_eye_tracker)
    thread_stimuli = threading.Thread(target=run_stimuli_experiment)

    # Start threads
    #thread_eye.start()
    thread_stimuli.start()

    # Wait for both threads to complete
    #thread_eye.join()
    thread_stimuli.join()
