
from main import MainRunner
from typing import Tuple, Callable, Type, List, Optional, Dict, Any, Union
from algorithms.algorithm import Algorithm
from algorithms.basic_testing import BasicTesting
from algorithms.configuration.maps.map import Map
from maps import Maps
from algorithms.lstm.LSTM_tile_by_tile import BasicLSTMModule,OnlineLSTM
from algorithms.lstm.ML_model import MLModel
from simulator.services.debug import DebugLevel
from analyzer.analyzer import Analyzer
from generator.generator import Generator

#Might be redundant
from structures import Size
from simulator.services import services
import pickle
from simulator.services.services import Services, GenericServices
# planner implementations
from algorithms.classic.graph_based.a_star import AStar
from algorithms.classic.graph_based.bug1 import Bug1
from algorithms.classic.graph_based.bug2 import Bug2
from algorithms.classic.graph_based.dijkstra import Dijkstra
from algorithms.classic.sample_based.sprm import SPRM
from algorithms.classic.sample_based.rt import RT
from algorithms.classic.sample_based.rrt import RRT
from algorithms.classic.sample_based.rrt_star import RRT_Star
from algorithms.classic.sample_based.rrt_connect import RRT_Connect
from algorithms.classic.graph_based.wavefront import Wavefront
from algorithms.configuration.configuration import Configuration
from algorithms.lstm.LSTM_tile_by_tile import OnlineLSTM
from algorithms.lstm.a_star_waypoint import WayPointNavigation
from algorithms.lstm.combined_online_LSTM import CombinedOnlineLSTM
from algorithms.lstm.LSTM_CAE_tile_by_tile import CAE,LSTMCAEModel


# planner testing
from algorithms.basic_testing import BasicTesting
from algorithms.classic.testing.a_star_testing import AStarTesting
from algorithms.classic.testing.combined_online_lstm_testing import CombinedOnlineLSTMTesting
from algorithms.classic.testing.dijkstra_testing import DijkstraTesting
from algorithms.classic.testing.wavefront_testing import WavefrontTesting
from algorithms.classic.testing.way_point_navigation_testing import WayPointNavigationTesting


#Dictionaries of possible options
from main_gui import GUI


config = type(Configuration)

config = Configuration()

maps = {
    "Uniform Random Fill": ("uniform_random_fill_10/0", True),
    "Block": ("block_map_10/6", True),
    "House": ("house_10/6", True),
    "Long Wall": (Maps.grid_map_labyrinth2, True),
    "Labyrinth": (Maps.grid_map_labyrinth, True),
    "Small Obstacle": (Maps.grid_map_one_obstacle.convert_to_dense_map(), True),
    "SLAM Map 1": ("map10", False),
    "SLAM Map 1 (compressed)": ("map11", True),
    "SLAM Map 2": ("map14", False),
    "SLAM Map 3": ("map12", False),
    "House Expo Sample": ("_house_expo/10",False)
    }

#LSTM Bagging is referred to as CombinedOnlineLSTM, it is used as a glboal kernel for WPN


algorithms = {
    "A*": (AStar, AStarTesting, ([], {})),
    "Global Way-point LSTM": (WayPointNavigation, WayPointNavigationTesting, ([], {"global_kernel": (CombinedOnlineLSTM, ([], {})), "global_kernel_max_it": 100})),
    "LSTM Bagging": (CombinedOnlineLSTM, CombinedOnlineLSTMTesting, ([], {})),
    "CAE Online LSTM": (OnlineLSTM, BasicTesting, ([], {"load_name": "caelstm_section_lstm_training_block_map_10000_model"})),
    "Online LSTM": (OnlineLSTM, BasicTesting, ([], {"load_name": "tile_by_tile_training_uniform_random_fill_10000_block_map_10000_house_10000_model"})),
    "SPRM": (SPRM, BasicTesting, ([], {})),
    "RT": (RT, BasicTesting, ([], {})),
    "RRT": (RRT, BasicTesting, ([], {})),
    "RRT*": (RRT_Star, BasicTesting, ([], {})),
    "RRT-Connect": (RRT_Connect, BasicTesting, ([], {})),
    "Wave-front": (Wavefront, WavefrontTesting, ([], {})),
    "Dijkstra": (Dijkstra, DijkstraTesting, ([], {})),
    "Bug1": (Bug1, BasicTesting, ([], {})),
    "Bug2": (Bug2, BasicTesting, ([], {})),
}

animations = {
    "None": (0, 0),
    "Normal": (0.00001, 0),
    "Slow": (0.5, 0),
    "Fast": (0.00001, 20)
}

debug = {
    "None": DebugLevel.NONE,
    "Basic": DebugLevel.BASIC,
    "Low": DebugLevel.LOW,
    "Medium": DebugLevel.MEDIUM,
    "High": DebugLevel.HIGH,
}

gen_maps = {
    "Uniform Random Fill" : "uniform_random_fill",
    "Block":"block_map",
    "House" : "house"
}

labelling = {
    BasicLSTMModule: [[
    "distance_to_goal_normalized",
    "raycast_8_normalized",
    "direction_to_goal_normalized",
    "agent_goal_angle"],['next_position_index'],[],[]],
    CAE: [[],[],['global_map'],['global_map']],
    LSTMCAEModel: [[],[],['global_map'],['global_map']]
    
    } 


#Input hyperparametres here 
chosen_map = 'House'
algo = algorithms['A*'] #Choose which planner 
ani = animations['Fast'] #Choose animation speed
debug = debug['High'] #Choose debug level 
training_algo = BasicLSTMModule #Chooses the algorithm to train, either CAE, BasicLSTMModule,LSTMCAEModel
nbr_ex = 100 #Number of maps generated
show_sample_map = False #shows 5 samples
gen_start = True
train_start = True
sim_start = False
analyzer_start = False
config.generator_house_expo = False
config.generator_size = 64
#Cache
config.clear_cache = True

#Generator
mp = maps[chosen_map] 

#Simulator
config.load_simulator = sim_start
config.simulator_graphics = True
config.simulator_initial_map, config.simulator_grid_display = mp
config.simulator_algorithm_type, config.simulator_testing_type, config.simulator_algorithm_parameters = algo
config.simulator_key_frame_speed, config.simulator_key_frame_skip = ani
config.simulator_write_debug_level = debug

#Generator
config.generator = gen_start
if config.generator_house_expo:
    gen_map = '_house_expo'
    config.generator_labelling_atlases = [gen_map]
    config.generator_nr_of_examples = nbr_ex

elif gen_start:
    gen_map = gen_maps[chosen_map]
    config.generator_labelling_atlases = [gen_map + '_' + str(nbr_ex)]

    config.generator_nr_of_examples = nbr_ex
    config.generator_gen_type = gen_map

#These are for training
config.generator_labelling_features = labelling[training_algo][0]
config.generator_labelling_labels =  labelling[training_algo][1]
config.generator_single_labelling_features = labelling[training_algo][2]
config.generator_single_labelling_labels = labelling[training_algo][3]

config.generator_aug_labelling_features = []
config.generator_aug_labelling_labels = []
config.generator_aug_single_labelling_features = []
config.generator_aug_single_labelling_labels = []
config.generator_modify = None
config.generator_show_gen_sample = show_sample_map

#Trainer
config.trainer = train_start
config.trainer_model = training_algo #Either BasicLSTMModule or CAE or LSTMCAEModel
config.trainer_custom_config = None
config.trainer_pre_process_data_only = False
config.trainer_bypass_and_replace_pre_processed_cache = False

#Analyzer
config.analyzer = analyzer_start

MainRunner(config).run_multiple()

#To generate map from image
# map_gen_from_img = False

# if map_gen_from_img == True:
#     Services = Services(config)
#     generated_map = Generator(Services)
#     generated_map.generate_map_from_image("map1.png",True,2)
