#!/usr/bin/env python3
"""
File:          Game.py
Author:        Alex Cui
Last Modified: Binit on 10/30
"""

import os
import pybullet as p

from simulator.field import Field
from simulator.racecar_agent import RacecarAgent


class Game:
    """Maintains and coordinates the game loop"""

    def __init__(self):
        """Initializes game elements
        Sets up game and simulation elements. For example,
        the three minute timer of the game.
        """
        self.cwd = os.getcwd()
        self.cid = p.connect(p.SHARED_MEMORY)
        if (self.cid < 0):
            p.connect(p.GUI)

        p.resetSimulation()
        p.setGravity(0, 0, -9.8)
        self.useRealTimeSim = 1

        #for video recording (works best on Mac and Linux, not well on Windows)
        #p.startStateLogging(p.STATE_LOGGING_VIDEO_MP4, "racecar.mp4")
        p.setRealTimeSimulation(self.useRealTimeSim)  # either this

        self.agent = RacecarAgent()
        self.field = Field()

    def load_statics(self):
        """Loading the static objects
        Including field, buttons, and more.
        """
        self.field.load_field_urdf(self.cwd)

    def load_agents(self):
        """Loading the agents
        Including the button robot and the mobile block stacking robot.
        """
        self.agent.load_racecar_urdf(self.cwd)

    def load_ui(self):
        """Loading the UI components
        Such as sliders or buttons.
        """
        self.maxForceSlider = p.addUserDebugParameter("maxForce", 0, 50, 20)

    def read_ui(self):
        """Reads the UI components' state
        And publishes them for all of game to process
        """
        maxForce = p.readUserDebugParameter(self.maxForceSlider)
        self.agent.set_max_force(maxForce)

    def process_keyboard_events(self):
        """Read keyboard events
        And publishes them for all of game to process
        """
        keys = p.getKeyboardEvents()
        if keys.get(65297): #up
            self.agent.increaseTargetVel()
        elif keys.get(65298): #down
            self.agent.decreaseTargetVel()
        else:
            self.agent.normalizeTargetVel()

        if keys.get(65296): #right
            self.agent.increaseRightSteering()
        elif keys.get(65295): #left
            self.agent.increaseLeftSteering()
        else:
            self.agent.normalizeSteering()

    def monitor_buttons(self):
        for i, b in enumerate(self.field.buttons.button_state):
            if p.getJointState(b.button, 1)[0] < -0.0038:
                self.field.buttons.press_button(i)
            else:
                self.field.buttons.unpress_button(i)
        
        # if p.getJointState(self.button1, 1)[0] < -0.038:
        #     # print("pressed")
        #     p.changeVisualShape(self.button1, 1, rgbaColor=[1, 1, 1, 1])

        # else:
        #     # print('not pressed')
        #     p.changeVisualShape(self.button1, 1, rgbaColor=[1, 1, 1, 0.8])


    def run(self):
        """Maintains the game loop
        Coordinates other functions to execute here and
        tracks the delta time between each game loop.
        """
        self.load_statics()
        self.load_agents()
        self.load_ui()

        while True:
            self.read_ui()
            self.process_keyboard_events()
            self.monitor_buttons()
            self.agent.update_racecar()
            self.field.buttons.update_buttons(1 / 240)
            # print(f"buttons state: in_sequence?={self.field.buttons.in_sequence} num_sequenced={self.field.buttons.num_sequenced} extra_sequenced={self.field.buttons.extra_not_sequenced}")

            if (self.useRealTimeSim == 0):
                p.stepSimulation()
