import csv
import datetime

from psychopy import visual, event, core

import BoxColors
from PairGen import generate_pairs
import os


def main():
    done = False

    # Loop enforces numeric input for recording participant numbers
    participant_num = -1
    while not done:
        try:
            participant_num = int(input("Please enter the numeric participant code: "))
            done = True
        except ValueError:
            print("Please enter a number")
        except Exception as e:
            print(e.message)
            print("If you wish to forcibly exit, press Ctrl+C (Cmd+C on a Mac)")

    display_type = None
    done = False
    while not done:
        # Checks for display type from user; stripes whitespace and converts to lowercase before storing
        display_type = input("Please enter 'p' for patches or 'm' for monitor: ").strip().lower()
        if display_type in ['p', 'm']:
            done = True
        else:
            print("Your input was neither 'p' nor 'm'; try again (or press Ctrl+C or Cmd+C to forcibly exit)")

    mds_type = None
    done = False
    while not done:
        # Checks for recording type from user; stripes whitespace and converts to lowercase before storing
        mds_type = input("Please enter 'a' for adjacent pairs or 'f' for full mds: ").strip().lower()
        if mds_type in ['a', 'f']:
            done = True
        else:
            print("Your input was neither 'a' nor 'f'; try again (or press Ctrl+C or Cmd+C to forcibly exit)")

    num_hues = 20
    num_contrast_levels = 1
    num_greys = 0
    total_colors = num_hues * num_contrast_levels + num_greys

    # Will generate a randomly ordered list of tuple pairs. Adjacent pairs compares greys with the lowest contrast level
    #   Note: If greys are included, it is assumed the lowest contrast level is the first X hues, where X is the number
    #   of hues per contrast level (num_hues). Greys will be the last Y numbers.
    #     So, in an adjacent pairs experiment, a comparison of (4, 21) is valid (4th hue compared to 1st grey if
    #     greys are enabled and there are 20 hues and 1 contrast level or 10 hues and 2 contrast levels, etc.)
    pairs = generate_pairs(mds_type, num_hues, num_contrast_levels, num_greys)

    responses = list()  # empty list to record responses in
    response_times = list()  # empty list to record response times
    # lists to record left and right display colors
    left_list = list()
    right_list = list()

    # === SETUP SCREEN AND RUN ===
    win = visual.Window(
        color=[-1, -1, -1],  # black
        fullscr=True,  # important for consistent timing and to focus participant on stimuli being presented
        allowGUI=False,  # gets rid of minimize, maximize, and close buttons at top of window (press ESC to exit)
        winType="pyglet",  # feel free to take this out; hardcoded for consistency, but should default to pyglet anyhow
        # NOTE: pygame windows will NOT record response times, so do not use pygame for winType
        units="pix"  # ensures use of pixels for units of screen
    )

    # Create list of numeric response keys; works with both number pad and main number bar at top of keyboard
    # currently creates list of keys 0-9. Can be adjusted by altering range() (remember, the end of range() is
    # non-inclusive, so add one to it; range(10) generates a range [0, 10), which is equivalent to [0, 9])
    #   NOTE: there are reported issues with number pad support on Windows, but should work on Mac and Linux
    resp_keys = ["{}".format(str(x)) for x in range(10)] + ["num_{}".format(str(x)) for x in range(10)]
    resp_keys.append("escape")  # important for early exit

    pause_trial = len(pairs) // 4  # see line below this one...
    pause_blocks = [pause_trial, pause_trial * 2, pause_trial * 3]  # used to determine built-in breaks during full MDS

    clock = core.Clock()  # used for recording reaction times; reset to 0 whe stimulus is drawn on  screen

    try:  # try running the experiment; if an error occurs it will catch it, print an error message,
        # then close the window. WARNING: If you take out the try/except/finally blocks you may end up stuck in
        # a full screen window with no way out.
        if display_type == 'p':  # if using patches
            for trial in range(len(pairs)):
                if mds_type == 'f' and trial in pause_blocks:  # gives break at 1/4, 1/2, and 3/4 way through full MDS
                    message = visual.TextStim(
                        win,
                        text="Take a break. Press any button to continue when you're ready."
                    )
                    message.draw()
                    win.flip()
                    event.waitKeys()  # waits until any button is pressed.
                    # can switch to timer, but remember to update message text if you do!

                left, right = pairs[trial][0], pairs[trial][1]
                message = visual.TextStim(
                    win,
                    "{0:d}{1:7d}".format(left, right),  # the number before the 'd' is the number of
                    # spaces before it if the pair is (3, 4) it will create a string '3     4' if the number after 1: is
                    # 5. The d means decimal (base 10) integer, the 0 and 1 mean the first and second argument
                    # (respectively) in the .format() method will be placed where the curly braces are.
                    #    NOTE: this string formatting style is used since it works with all of python 3 and python 2.7,
                    #    but it can be replaced by another formatting style if one so desires.
                    height=100
                )
                message.draw()
                win.flip()

                clock.reset()  # resets time to 0 immediately after stimuli are shown on screen

                keypress = event.waitKeys(keyList=resp_keys, timeStamped=clock)  # returns: (key, timestamp)
                if keypress[0][0] == 'escape':
                    raise KeyboardInterrupt
                responses.append(keypress[0][0])  # records what key was pressed
                response_times.append(round(keypress[0][1], 2))  # records response time down to 100th of a second
                left_list.append(left)  # records numeric code for left color displayed
                right_list.append(right)  # records numeric code for right color displayed

        elif display_type == 'm':  # monitor version
            # For now, this chunk of code is largely identical to the patches version except with two box stims instead
            # of one text stim. Ideally, we should figure out a way to not have so much repeated code so that we can
            # make changes to both versions at once, but for now this will do.

            colors = BoxColors.colors  # dict of colors ; update BoxColors.py if you change color selection

            for trial in range(len(pairs)):
                if mds_type == 'f' and trial in pause_blocks:  # gives break at 1/4, 1/2, and 3/4 way through full MDS
                    message = visual.TextStim(
                        win,
                        text="Take a break. Press any button to continue when you're ready."
                    )
                    message.draw()
                    win.flip()
                    event.waitKeys()  # waits until any button is pressed.
                    # can switch to timer, but remember to update message text if you do!

                left, right = pairs[trial][0], pairs[trial][1]
                box = visual.Rect(
                    win,
                    width=75,
                    height=100,
                    pos=[125, 0],
                    lineWidth=0
                )
                box.fillColor = colors[left]  # my IDE freaks out when I pass this in as a parameter to the constructor
                # above, which is why I place it here outside the initial Rect() constructor.

                box.draw()

                box.pos = [-125, 0]
                box.fillColor = colors[right]
                box.draw()

                win.flip()

                clock.reset()  # resets time to 0 immediately after stimuli are shown on screen

                keypress = event.waitKeys(keyList=resp_keys, timeStamped=clock)  # returns: (key, timestamp)
                if keypress[0][0] == 'escape':
                    raise KeyboardInterrupt
                responses.append(keypress[0][0])  # records what key was pressed
                response_times.append(round(keypress[0][1], 2))  # records response time down to 100th of a second
                left_list.append(left)  # records numeric code for left color displayed
                right_list.append(right)  # records numeric code for right color displayed

    except Exception as e:  # prints corresponding error message to python console if an error occurs
        try:
            print(e.message)  # some errors do not have a message attribute, hence the nested try/except
        except:
            print("ESC was pressed or an unknown error may have occurred")

    else:  # if user did not abort by pressing ESC and an error did not occur
        # Create filename format
        #   EXAMPLE:
        #        Let's say the display type is monitor, participant number is 1, mds type is full MDS, and time of
        #        completion is 18:23 on June 7, 2020.
        #        The resulting filename will then be 'm_1_f_2020-06-07_18-23'
        filename = '_'.join([display_type,
                             str(participant_num),
                             mds_type,
                             str(datetime.datetime.now())[:-10].replace(':', '-').replace(' ', '_')
                             ])
        print(filename)  # debug
        # Create csv (spreadsheet) file stored in output directory5
        with open('.' + os.path.join(os.sep, "output", "{}.csv".format(filename)), 'w', newline="") as fh:
            csvwriter = csv.writer(fh)
            csvwriter.writerow(["left_color", "right_color", "response", "time"])  # Column titles
            csvwriter.writerows([[left_list[x], right_list[x], responses[x], response_times[x]] for x in
                                 range(len(pairs))])

    finally:  # closes window regardless of errors (IF YOU TAKE THIS OUT THE WINDOW WILL NOT CLOSE IF AN ERROR OCCURS)
        win.close()
        core.quit()


if __name__ == '__main__':
    main()
