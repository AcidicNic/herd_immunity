import random, sys
random.seed(42)
from person import Person
from logger import Logger
from virus import Virus


class Simulation(object):
    ''' Main class that will run the herd immunity simulation program.
    Expects initialization parameters passed as command line arguments when file is run.

    Simulates the spread of a virus through a given population.  The percentage of the
    population that are vaccinated, the size of the population, and the amount of initially
    infected people in a population are all variables that can be set when the program is run.
    '''
    def __init__(self, pop_size, vacc_percentage, virus, initial_infected=1):
        ''' Logger object logger records all events during the simulation.
        Population represents all Persons in the population.
        The next_person_id is the next available id for all created Persons,
        and should have a unique _id value.
        The vaccination percentage represents the total percentage of population
        vaccinated at the start of the simulation.
        You will need to keep track of the number of people currently infected with the disease.
        The total infected people is the running total that have been infected since the
        simulation began, including the currently infected people who died.
        You will also need to keep track of the number of people that have die as a result
        of the infection.

        All arguments will be passed as command-line arguments when the file is run.
        HINT: Look in the if __name__ == "__main__" function at the bottom.
        '''
        # TODO: Store each newly infected person's ID in newly_infected attribute.
        # At the end of each time step, call self._infect_newly_infected()
        # and then reset .newly_infected back to an empty list.
        self.pop_size = pop_size # Int
        self.next_person_id = 0 # Int
        self.virus = virus # Virus object
        self.initial_infected = initial_infected # Int
        self.total_infected = 0 # Int
        self.current_infected = 0 # Int
        self.vacc_percentage = vacc_percentage # float between 0 and 1
        self.total_dead = 0 # Int
        self.people_dead = 0
        self.newly_infected = []
        self.alive_infected = []
        self.file_name = "{}_simulation_pop_{}_vp_{}_infected_{}.txt".format(
            virus_name, pop_size, vacc_percentage, initial_infected)
        self.population = self._create_population(initial_infected) # List of Person objects
        self.logger = Logger(self.file_name)

    def _create_population(self, initial_infected):
        '''This method will create the initial population.
            Args:
                initial_infected (int): The number of infected people that the simulation
                will begin with.

            Returns:
                list: A list of Person objects.

        '''
        vaccinated_count = int(self.vacc_percentage * self.pop_size)
        pop = []

        for i in range(self.pop_size):
            if initial_infected > 0:
                pop.append(Person(self.next_person_id, False, self.virus))
                self.newly_infected.append(self.next_person_id)
                initial_infected -= 1
            elif vaccinated_count > 0:
                pop.append(Person(self.next_person_id, True))
                vaccinated_count -= 1
            else:
                pop.append(Person(self.next_person_id, False))
            self.next_person_id += 1
        return pop

    def _simulation_should_continue(self):
        ''' The simulation should only end if the entire population is dead
        or everyone is vaccinated.

            Returns:
                bool: True for simulation should continue, False if it should end.
        '''
        for person in self.population:
            if person.is_alive:
                if not person.is_vaccinated:
                    return True
        return False

    def run(self):
        ''' This method should run the simulation until all requirements for ending
        the simulation are met.
        '''
        time_step_counter = 0
        self.logger.write_metadata(self.pop_size, self.vacc_percentage, self.virus.name,
                                   self.virus.mortality_rate, self.virus.repro_rate)

        while self._simulation_should_continue():
            self.time_step()
            self.logger.log_time_step(time_step_counter, self.current_infected, self.people_dead, self.total_infected, self.total_dead, self.pop_size)
            time_step_counter += 1
        print(f'The simulation has ended after {time_step_counter} turns.')

    def time_step(self):
        ''' This method should contain all the logic for computing one time step
        in the simulation.

        This includes:
            1. 100 total interactions with a random person for each infected person
                in the population
            2. If the person is dead, grab another random person from the population.
                Since we don't interact with dead people, this does not count as an interaction.
            3. Otherwise call simulation.interaction(person, random_person) and
                increment interaction counter by 1.
            '''

        self.people_dead = 0
        # loops through the id (index) of all infected people
        for index in self.alive_infected:
            person = self.population[index]
            if person.is_alive:
                # 100 interactions for each infected person
                for i in range(100):
                    # find a random person that is alive and isn't the same person
                    random_person = random.choice(self.population)
                    while random_person is person or not random_person.is_alive:
                        random_person = random.choice(self.population)

                    # person and random_person interact
                    self.interaction(person, random_person)
                # checks if the infected person survived the infection
                if not person.did_survive_infection():
                    person.is_alive = False
                    self.total_dead += 1
                    self.alive_infected.remove(person._id)
                    self.people_dead += 1
        self._infect_newly_infected()

    def interaction(self, person, random_person):
        '''This method should be called any time two living people are selected for an
        interaction. It assumes that only living people are passed in as parameters.

        Args:
            person (person): The initial infected person
            random_person (person): The person that person1 interacts with.
        '''
        # Assert statements are included to make sure that only living people are passed
        # in as params
        assert person.is_alive == True
        assert random_person.is_alive == True

        if random_person.is_vaccinated:
            # nothing happens to random person.
            self.logger.log_interaction(person, random_person, False, True, False)
        elif random_person.infection is not None:
            # nothing happens to random person.
            self.logger.log_interaction(person, random_person, True, False, False)
        else:
            if random.random() <  self.virus.repro_rate:
                # random person is infected.
                self.newly_infected.append(random_person._id)
                self.logger.log_interaction(person, random_person, False, False, True)
            else:
                # nothing happens to random person.
                self.logger.log_interaction(person, random_person, False, False, False)

    def _infect_newly_infected(self):
        ''' This method should iterate through the list of ._id stored in self.newly_infected
        and update each Person object with the disease. '''
        self.current_infected = 0
        for index in self.newly_infected:
            self.alive_infected.append(index)
            self.population[index].infection = self.virus
            self.current_infected += 1
        self.newly_infected = []
        self.total_infected += self.current_infected


if __name__ == "__main__":
    # params = sys.argv[1:]
    params = ["HIV", .8, .3, 900, .1, 50]
    virus_name = str(params[0])
    repro_num = float(params[1])
    mortality_rate = float(params[2])

    pop_size = int(params[3])
    vacc_percentage = float(params[4])

    if len(params) == 6:
        initial_infected = int(params[5])
    else:
        initial_infected = 1

    virus = Virus(virus_name, repro_num, mortality_rate)
    sim = Simulation(pop_size, vacc_percentage, virus, initial_infected)

    sim.run()
