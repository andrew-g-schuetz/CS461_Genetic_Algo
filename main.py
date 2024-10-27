import random
import numpy as np
from scipy.special import softmax

activities = [
    {
        "name": "SLA100A",
        "expected_enrollment": 50,
        "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"],
        "other_facilitators": ["Numen", "Richards"]
    },
    {
        "name": "SLA100B",
        "expected_enrollment": 50,
        "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"],
        "other_facilitators": ["Numen", "Richards"]
    },
    {
        "name": "SLA191A",
        "expected_enrollment": 50,
        "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"],
        "other_facilitators": ["Numen", "Richards"]
    },
    {
        "name": "SLA191B",
        "expected_enrollment": 50,
        "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"],
        "other_facilitators": ["Numen", "Richards"]
    },
    {
        "name": "SLA201",
        "expected_enrollment": 50,
        "preferred_facilitators": ["Glen", "Banks", "Zeldin", "Shaw"],
        "other_facilitators": ["Numen", "Richards", "Singer"]
    },
    {
        "name": "SLA291",
        "expected_enrollment": 50,
        "preferred_facilitators": ["Lock", "Banks", "Zeldin", "Singer"],
        "other_facilitators": ["Numen", "Richards", "Shaw", "Tyler"]
    },
    {
        "name": "SLA303",
        "expected_enrollment": 60,
        "preferred_facilitators": ["Glen", "Zeldin", "Banks"],
        "other_facilitators": ["Numen", "Singer", "Shaw"]
    },
    {
        "name": "SLA304",
        "expected_enrollment": 25,
        "preferred_facilitators": ["Glen", "Banks", "Tyler"],
        "other_facilitators": ["Numen", "Singer", "Shaw", "Richards", "Uther", "Zeldin"]
    },
    {
        "name": "SLA394",
        "expected_enrollment": 20,
        "preferred_facilitators": ["Tyler", "Singer"],
        "other_facilitators": ["Richards", "Zeldin"]
    },
    {
        "name": "SLA449",
        "expected_enrollment": 60,
        "preferred_facilitators": ["Tyler", "Singer", "Shaw"],
        "other_facilitators": ["Zeldin", "Uther"]
    },
    {
        "name": "SLA451",
        "expected_enrollment": 100,
        "preferred_facilitators": ["Tyler", "Singer", "Shaw"],
        "other_facilitators": ["Zeldin", "Uther", "Richards", "Banks"]
    }
]

facilitators = ["Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"]


rooms = [
    {"name": "Slater 003", "capacity": 45},
    {"name": "Roman 216", "capacity": 30},
    {"name": "Loft 206", "capacity": 75},
    {"name": "Roman 201", "capacity": 50},
    {"name": "Loft 310", "capacity": 108},
    {"name": "Beach 201", "capacity": 60},
    {"name": "Beach 301", "capacity": 75},
    {"name": "Logos 325", "capacity": 450},
    {"name": "Frank 119", "capacity": 60}
]

time_slots = ["10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM"]

population_size = 500
mutation_rate = .01
num_generations = 100

#Creates a population list with random attributes of the above schedule requirements
def initialize_population():
    population = []
    for _ in range(population_size):
        schedule = []
        for activity in activities:
            assigned_room = random.choice(rooms)
            assigned_time = random.choice(time_slots)
            assigned_facilitator = random.choice(facilitators)
            schedule.append({"activity": activity["name"], 
                             "room": assigned_room, 
                             "time": assigned_time, 
                             "facilitator": assigned_facilitator, 
                             "expected_enrollment": activity["expected_enrollment"]})
        
        population.append(schedule)
    return population

def fitness_score_calculator(schedule):
    fitness = 0

    facilitator_scheduled = {facilitator:0 for facilitator in facilitators}

    scheduled_events = {}

    SLA100_times = []
    SLA191_times = []

    for event in schedule:
        activity_name = event["activity"]
        # Find the activity details using the name
        activity = next((a for a in activities if a["name"] == activity_name), None)

        if activity is None:
            continue

        time_room = (event["time"], event["room"]["name"])
        if time_room in scheduled_events:
            fitness -=0.5
        else:
            scheduled_events[time_room] = event["activity"]
        
        #room size
        room_capacity = event["room"]["capacity"]
        if room_capacity < activity["expected_enrollment"]:
            fitness-=0.5
        elif room_capacity > 3 * activity["expected_enrollment"]:
            fitness-=0.2
        elif room_capacity > 6 * activity["expected_enrollment"]:
            fitness-=0.4
        else:
            fitness+=0.3

        #preferred facilitators
        if event["facilitator"] in activity["preferred_facilitators"]:
            fitness+=0.5
        elif event["facilitator"] in activity["other_facilitators"]:
            fitness+=0.2
        else:
            fitness-=0.1

        facilitator_scheduled[event["facilitator"]]+=1

        if facilitator_scheduled[event["facilitator"]] > 4:
            fitness-=0.5
        elif facilitator_scheduled[event["facilitator"]] in [1,2]:
            fitness-=0.4
        
        if event["facilitator"] == "Tyler" and facilitator_scheduled[event["facilitator"]] > 2:
            fitness+=0

        if event["activity"] in ["SLA100A", "SLA100B"]:
            SLA100_times.append(event)
        elif event["activity"] in ["SLA191A", "SLA191B"]:
            SLA191_times.append(event)

    if len(SLA100_times) == 2:
        time_index = [time_slots.index(x["time"]) for x in SLA100_times]
        if abs(time_index[0] - time_index[1]) > 4:
            fitness+=0.5
        elif time_index[0] == time_index[1]:
            fitness-=0.5
        
    if len(SLA191_times) == 2:
        time_index = [time_slots.index(x["time"]) for x in SLA191_times]
        if abs(time_index[0] - time_index[1]) > 4:
            fitness+=0.5
        elif time_index[0] == time_index[1]:
            fitness-=0.5
        
    for SLA100 in SLA100_times:
        for SLA191 in SLA191_times:
            SLA100_time_index = time_slots.index(SLA100["time"])
            SLA191_time_index = time_slots.index(SLA191["time"])

            if abs(SLA100_time_index - SLA191_time_index) == 1:
                fitness+=0.5
                if(SLA100["room"]["name"].startswith("Roman") or SLA100["room"]["name"].startswith("Beach")) and \
                    not (SLA191["room"]["name"].startswith("Roman") or SLA191["room"]["name"].startswith("Beach")):
                    fitness-=0.4
                elif (SLA191["room"]["name"].startswith("Roman") or SLA191["room"]["name"].startswith("Beach")) and \
                     not (SLA100["room"]["name"].startswith("Roman") or SLA100["room"]["name"].startswith("Beach")):
                    fitness -= 0.4
            
            if abs(SLA100_time_index - SLA191_time_index) == 2:
                fitness+=0.25
            if SLA100_time_index == SLA191_time_index:
                fitness-=0.25
    
    return fitness

def mutate(schedule):
    new_schedule = schedule.copy()

    for event in new_schedule:
        if random.random() < mutation_rate:
            mutation_type = random.choice(["room", "time", "facilitator"])

            if mutation_type == "room":
                event["room"] = random.choice(rooms)
            elif mutation_type == "time":
                event["time"] = random.choice(time_slots)
            elif mutation_type == "facilitator":
                event["facilitator"] = random.choice(facilitators)
    
    return new_schedule
    """if random.random() < mutation_rate:
        index = random.randint(0,len(new_schedule)-1)
        new_schedule[index]["room"] = random.choice(rooms)
        new_schedule[index]["time"] = random.choice(time_slots)
        new_schedule[index]["facilitator"] = random.choice(facilitators)

    return new_schedule"""

def crossover(parent_one, parent_two):
    crossover_point = random.randint(0,len(parent_one)-1)

    child = parent_one[:crossover_point] + parent_two[crossover_point:]
    return child

def genetic_algorithm():
    population = initialize_population()

    for generation in range(num_generations):

        fitness_scores = [fitness_score_calculator(schedule) for schedule in population]

        probabilities = softmax(fitness_scores)

        new_population = []

        for _ in range(population_size):
            parent_one_index = np.random.choice(range(population_size), p=probabilities)
            parent_two_index = np.random.choice(range(population_size), p=probabilities)
            parent_one = population[parent_one_index]
            parent_two = population[parent_two_index]

            child = crossover(parent_one, parent_two)

            child = mutate(child)

            new_population.append(child)

        population = new_population

        best_fitness = max(fitness_scores)
        print(f"Generation {generation+1}: Best fitness = {best_fitness}")

    best_schedule_index = fitness_scores.index(max(fitness_scores))
    return population[best_schedule_index], fitness_scores[best_schedule_index]

best_schedule, best_fitness = genetic_algorithm()

output_file = "best_schedule.txt"
with open(output_file, 'w') as f:
    f.write("Best Schedule:\n")
    for event in best_schedule:
        f.write(f"Activity: {event['activity']}, Room: {event['room']['name']}, Time: {event['time']}, Facilitator: {event['facilitator']}\n")
    f.write(f"Best Fitness: {best_fitness}\n")

print(f"Results written to {output_file}")

        


        

    

