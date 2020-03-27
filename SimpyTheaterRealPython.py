"""Simulation of wait times in a theater to choose an cost effective number of employees
and keeping the wait time as bearable as possible.
Average bearable wait time for a customer is 10 min from Reviews.
An average moviegoer goes like:-
1) Arrive at the theater, get in line, and wait to purchase a ticket.
2) Buy a ticket from the box office.
3) Wait in line to have the ticket checked.
4) Get the ticket checked by an usher.
5) Choose whether or not to get in line for the concession stand:
   a) If they get in line, then they purchase food.
   b) If they don’t get in line, then they skip to the last step.
6) Go find their seat."""

# Setting up the Environment
import simpy
import random
import statistics

# A List to contain the wait times
wait_times = []


# Creating Environment: Class Definition
# Cashiers are a resource that the theater makes available to its customers,
# and they help moviegoers through the process of purchasing a ticket.
class Theater(object):
    def __init__(self, env, num_cashiers, num_servers, num_ushers):
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers)
        self.server = simpy.Resource(env, num_servers)
        self.usher = simpy.Resource(env, num_ushers)

    # env.timeout() tells simpy to trigger an event after a certain amount of time has passed.
    # In this case, the event is that a ticket was purchased.
    def purchase_ticket(self, moviegoer):
        yield self.env.timeout(random.uniform(1, 3))

    def check_ticket(self, moviegoer):
        yield self.env.timeout(0.05)

    def sell_food(self, moviegoer):
        yield self.env.timeout(random.uniform(1, 5))


# Moving Through the Environment: Function Definition
# Alright, you’ve set up the environment by defining a class.
# You have resources and processes. Now you need a moviegoer to use them.
# When a moviegoer arrives at the theater, they’ll request a resource,
# wait for its process to complete, and then leave. You’ll create a function,
# called go_to_movies(), to keep track of this:
#
# Inputs
# env: The moviegoer will be controlled by the environment, so you’ll pass this as the first argument.
# moviegoer: This variable tracks each person as they move through the system.
# theater: This parameter gives you access to the processes you defined in the overall class definition.
def go_to_movies(env, moviegoer, theater):
    # Moviegoer arrives at the Theater
    arrival_time = env.now

    # You’ll want each of the processes from your theater to have corresponding requests in go_to_movies().
    # For example, the first process in the class is purchase_ticket(), which uses a cashier resource.
    # The moviegoer will need to make a request to the cashier resource to help them through the purchase_ticket()
    # process.
    #
    # theater.cashier.request(): moviegoer generates a request to use a cashier.
    # yield request: moviegoer waits for a cashier to become available if all are currently in use.
    # To learn more about the yield keyword, check out How to Use Generators and yield in Python.
    # yield env.process(): moviegoer uses an available cashier to complete the given process.
    # In this case, that’s to purchase a ticket with a call to theater.purchase_ticket().
    with theater.cashier.request() as request:
        yield request
        yield env.process(theater.purchase_ticket(moviegoer))

    with theater.usher.request() as request:
        yield request
        yield env.process(theater.check_ticket(moviegoer))

    # 40 Percent of people want the food inside the Theater
    # Output: food: The moviegoer will request a server and order food.
    #         no_food: The moviegoer will instead go to find their seats without purchasing any snacks.
    food_list = ['food', 'no_food']
    if 'food' in random.choices(food_list, weights=[0.4, 0.6], k=1):
        with theater.server.request() as request:
            yield request
            yield env.process(theater.sell_food(moviegoer))

    # moviegoer now goes into Theater
    # You use env.now to get the time at which the moviegoer has finished all processes and made it to their seats.
    # You subtract the moviegoer’s arrival_time from this departure time and append the resulting time difference
    # to your waiting list, wait_times.
    # You could store the departure time in a separate variable like departure_time,
    # but this would make your code very repetitive, which violates the Don't Repeat Yourself principle.
    wait_times.append(env.now - arrival_time)

# Define a function to run the simulation. run_theater() will be responsible for creating an instance of a theater
# and generating moviegoers until the simulation stops. The first thing this function should do is create an instance
# of a theater:
def run_theater(env, num_cashiers, num_servers, num_ushers ):
    theater = Theater(env, num_cashiers, num_servers, num_ushers)

    # You also might want to start your simulation with a few moviegoers waiting at the theater.
    # There will probably be a few people ready to go as soon as the doors open! The manager says to expect
    # around 3 moviegoers in line ready to buy tickets as soon as the box office opens. You can tell the
    # simulation to go ahead and move through this initial group like so:
    for moviegoer in range(5):
        env.process(go_to_movies(env, moviegoer, theater))

    # You don’t know how long it will take new moviegoers to make it to the theater, so you decide to look at
    # past data. Using timestamped receipts from the box office, you learn that moviegoers tend to arrive at the
    # theater, on average, every 12 seconds. Now all you have to do is tell the function to wait this long before
    # generating a new person:
    while True:
        yield env.timeout(0.2)
        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theater))

# At this point, you should have a list wait_times that contains the total amount of time it took each moviegoer to
# make it to their seat. Now you’ll want to define a function to help calculate the average time a moviegoer spends
# from the time they arrive to the time they finish checking their ticket. get_average_wait_time() does just this:
def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    return average_wait

# Since you’re creating a script that will be used by the movie theater manager, you’ll want to make sure that the
# output can be read easily by the user.
def calculate_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    minutes, frac_minutes = divmod(average_wait,1)
    seconds = frac_minutes*60
    # can use round() if we want
    return minutes, seconds
