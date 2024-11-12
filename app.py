import random
import brawlstars as bs
import matplotlib.pyplot as plt
import numpy as np
import math

#REPLACE WITH YOUR OWN (CAN BE MADE VIA BRAWLSTARSAPI.NET FOR FREE)
client = bs.Client("")

class User():
    #a class for the data of the player, initialised with their brawl stars tag
    def __init__(self, tag):
        player = client.get_player(tag)
        no_brawlers = len(player.brawlers)
        self.avg_trophies = round(player.trophies/no_brawlers,2)
        self.brawlers = player.brawlers
        trophies = []
        for x in player.brawlers:
            trophy = x.trophies
            trophies.append(trophy)
        self.trophies = trophies
    #initialises, by accessing the client using the player's tags, basic info stored
    
    def calculate_strength(self, brawler): #calculates the strength of a brawler
        
        if len(brawler.star_powers) > 0:
            hasStarPower = 1.2
        else:
            hasStarPower = 1.0
        if len(brawler.gadgets) > 0:
            hasGadget = 1.1
        else:
            hasGadget = 1.0
        gears = len(brawler.gears)
        gears = 0.000833*gears**3-0.0125*gears**2+0.06167*gears+0.99
        # realisticly, strength would be personalised per brawler based on the actual strength of the star power and gadget, as well as the brawler overall, but this is very hard to actually implement due to the sheer amount of dispute. Thus, values have been hard coded, and is based off of the build of the brawler, rather than how good the brawler is in the meta. There is room for improvement here, if anyone wants to help
        power = (1+(brawler.power-1)/10)
        description = f"Power level {brawler.power}, has {len(brawler.gadgets)} gadgets, {len(brawler.star_powers)} star powers, and {len(brawler.gears)} gears."
        strength = power*gears*hasGadget*hasStarPower
        # calculates strength -> currently this would mean that a maxed brawler is as strong as any other maxed brawler. Unfortunately, the API does not include hypercharges just yet, so it will not consider hypercharges.
        return round(strength,2)

    def strongest_brawlers(self):
        strengths = []
        for x in self.brawlers:
            strength = self.calculate_strength(x)
            strengths.append(strength)
        self.strengths = strengths
        #creates a list for all of the user's brawlers with their strength, sorting in descending order

    def standard_dev_strength(self):
        #assumes strongestBrawlers() has been called, as this wont be called by itself ever
        mean = sum(self.strengths)/len(self.strengths)
        copy_strengths = [n**2 for n in self.strengths.copy()]
        deviation = (sum(copy_strengths)/len(self.strengths)) - (mean**2)
        deviation = math.sqrt(deviation)
        self.deviation = deviation
        self.mean = mean
        #calculates standard deviation in strength

    def standard_dev_trophies(self):
        mean = sum(self.trophies)/len(self.trophies)
        mean_n_squared = sum([n**2 for n in self.trophies])/len(self.trophies)
        std_dev_trophies = math.sqrt(mean_n_squared - (mean**2))
        self.std_dev_trophies = std_dev_trophies
        
    def average_strength(self):
        #assumes strongestBrawlers() and standard_dev has been called, as this wont be called by itself ever
        exclude = self.mean - (self.deviation*2)
        count = len(self.strengths)
        total = 0
        for x in self.strengths:
            if x<exclude:
                count -=1
            else:
                total += x
        #excludes any brawlers whose strength is two std devs below the mean (mainly done to ignore any brawlers at pwr 1)
        avg_strength = total/count
        self.av_strength = round(avg_strength,2)

    def avg_strength(self):
        #wrapper function to find the average strength
        self.strongest_brawlers()
        self.standard_dev_strength()
        self.average_strength()
    
    def difficulty_to_push(self):
        difficulties = []
        #finds the difficutly to push each brawler based on tier lists (this can be easily improved if i had access to win rates of brawlers, but this requires special supercell permission which i do not have so it must be hardcoded)
        for x in self.brawlers:
            if x.name in ["DARRYL","ANGELO","GALE","MEG","FRANK","LARRY AND LAWRIE","LILY","CLANCY"]:
                difficulty = 1.07
            elif x.name in ["MORTIS","MOE","BERRY","BARLEY","SANDY","BYRON","KIT","MAX","COLETTE","GENE","PIPER","RICO","BUSTER","SURGE","CHESTER","R-T","AMBER","MELODIE"]:
                difficulty = 1.05
            elif x.name in ["TARA","SQUEAK","CORDELIUS","TICK","COLT","CROW","MANDY","8-BIT","BUZZ","CARL","JESSIE","NITA","STU","GRAY","DYNAMIKE","GRIFF","BELLE"]:
                difficulty= 1.01
            elif x.name in ["GUS","SPIKE","SPROUT","LOU","BROCK","EMZ","EVE","FANG","LEON","NANI","POCO","EL PRIMO","ROSA","RUFFS","SHELLY","SAM","WILLOW","PEARL","CHUCK","CHARLIE","MICO","DRACO","BIBI","JACKY","LOLA","EDGAR","OTIS","PAM"]:
                difficulty= 0.98
            elif x.name in ["BEA","BONNIE","MR. P","PENNY","GUS","MAISIE","BO","GROM","BULL","HANK"]:
                difficulty = 0.95
            elif x.name in ["ASH","JANET","DOUG"]:
                difficulty = 0.93
            else:
                difficulty = 1.0
            difficulties.append(difficulty)
        self.difficulties = difficulties


    def expected_trophies(self):
        if not getattr(self,"difficulties", None):
            self.difficulty_to_push()
        if not getattr(self,"av_strength", None):
            self.avg_strength()
        if not getattr(self,"strengths", None):
            self.strongest_brawlers()
        #call functions required beforehand

        expect_trophies = []
        for x in range(len(self.strengths)-1):
            num = random.randint(9900,10100)/10000
            expect_trophy = self.avg_trophies * (1+(self.strengths[x] - self.av_strength)) * self.difficulties[x] * num
            #calculates the expected trophies via
            #Expected = avg * deviation in strength * difficulty to push * random element (cos this is a game filled with luck and random events that cant be accounted for)
            if expect_trophy < 200:
                num = random.randint(8900,12100)/10000
                expect_trophy = 200 * num
            expect_trophy = round(expect_trophy)
            name = self.brawlers[x].name
            brawler = (expect_trophy,name)
            expect_trophies.append(brawler)
        #produces a list of expected trophies for every brawler with each item being a list or name and brawler
        self.expect_trophies = expect_trophies

    def highest_expected(self,num):
        if not getattr(self,"expect_trophies", None):
            self.expected_trophies()
        copy_expected = self.expect_trophies.copy()
        copy_expected.sort(reverse = True)
        for x in range(num):
            print(f"{x+1}. {copy_expected[x][1]} has an expected {copy_expected[x][0]} trophies")
        #prints highest n expected 

    def deviation_in_trophies(self):
        if not getattr(self,"expect_trophies", None):
            self.expected_trophies()
        deviations = []
        sm = 0
        for x in range(len(self.brawlers)-1):
            deviation = self.brawlers[x].trophies - self.expect_trophies[x][0]
            sm += deviation
            deviation = (deviation, self.brawlers[x].name)
            deviations.append(deviation)
        self.deviations = deviations
        average_deviation = sm/len(deviations)
        self.average_deviation = average_deviation
        #finds the deviation in trophies between exp and real, and the avg deviation

    def over_exceeding(self, num=10):
        if not getattr(self,"deviations", None):
            self.deviation_in_trophies()
        copy_devs = self.deviations.copy()
        copy_devs.sort(reverse=True)
        copy_devs = copy_devs[:num]
        for x in range(num):
            print(f"{x+1}. {copy_devs[x][-1]} is {copy_devs[x][0]} more trophies than expected.")
        #prints brawlers with the highest deviation

    def under_exceeding(self, num=10):
        if not getattr(self,"deviations", None):
            self.deviation_in_trophies()
        copy_devs = self.deviations.copy()
        copy_devs.sort()
        for x in range(num):
            print(f"{x+1}. {copy_devs[x][1]} is {-1*copy_devs[x][0]} less trophies than expected.")
        #prints brawlers wiht the lowest deviation

    def min_max_trophies(self):
        if not getattr(self,"std_dev_trophies",None):
            self.standard_dev_trophies()
        mn = 900
        mx = 0
        for x in self.brawlers:
            trophy = x.trophies
            if trophy>mx:
                mx = trophy
            elif trophy < mn and trophy > mn-self.std_dev_trophies:
                mn = trophy
        return mn, mx
        #find min max of trophies

    def min_max_exp_trophies(self):
        copy_expected = self.expect_trophies.copy()
        copy_expected.sort()
        mn = copy_expected[0][0]
        mx = copy_expected[-1][0]
        return mn, mx
        #find min max of expected

    def graph(self):
        if not getattr(self,"deviations", None):
            self.deviation_in_trophies()
        if not getattr(self, "deviation", None):
            self.avg_strength()
        if not getattr(self,"std_dev_trophies", None):
            self.standard_dev_trophies()
        #call prerequisite functions

        fig,ax = plt.subplots()
        for xs in range(len(self.brawlers)-1):
            exp = self.expect_trophies[xs][0]
            trophy = self.brawlers[xs].trophies
            x = [exp]
            y = [trophy]
            if trophy-exp> self.std_dev_trophies:
                clor = 'g'
            elif trophy-exp < (-1*self.std_dev_trophies):
                clor = 'r'
            else: 
                clor = 'black'
            plt.scatter(x,y,color = clor)
            #plot each brawler
        
        for xs in range(len(self.brawlers)-1):
            exp = self.expect_trophies[xs][0]
            trophy = self.brawlers[xs].trophies
            name = self.brawlers[xs].name
            if trophy-exp > self.std_dev_trophies or trophy-exp < -1*self.std_dev_trophies:
                plt.annotate(name, (exp, trophy), (exp, trophy)) 
            #label noteworthy brawlers

        # now plot both limits against eachother
        trophy_lims = self.min_max_trophies()
        exp_lims = self.min_max_exp_trophies()
        ax.set_ylim(trophy_lims[0]-10, trophy_lims[1]+10)
        ax.set_xlim(exp_lims[0],exp_lims[1])
        ax.plot((trophy_lims[0]-10,trophy_lims[0]-10), (trophy_lims[1]+10,trophy_lims[1]+10))
        #create limits so that the graph excludes most crazy anomalies
        plt.xlabel("Expected trophies")
        plt.ylabel("Actual Trophies")

        plt.show()
def main():
    done = False
    while not done:
        tag = input("Enter your brawl stars tag (don't forget the #): ")
        if "#" not in tag:
            tag = f"#{tag}"  # Ensure the tag has a '#'
        try:
            user = User(tag)
            done = True
        except e:
            print(e)
    user_done = False
    while not user_done:
        option = 0
        while option < 1 or option > 4:
            try:
                option = int(input("""Enter what you want to do:
            1. see over exceeding brawlers
            2. see under performing brawlers
            3. see top x highest expected brawlers
            4. see a graph of trophies vs expected """))
            except TypeError:  
                print("Incorrect input")
        if option == 1:
            user.over_exceeding()
        
        elif option == 2:
            user.under_exceeding()

        elif option == 3:
            n = 0
            while n < 1 or n > len(user.brawlers):
                try:
                    n = int(input("Enter number of brawlers: "))
                except: 
                    print("invalid input")
            user.highest_expected(n)
        
        else:
            user.graph()

        cont = input("Do you want to continue? [Y/N]")
        if cont.lower() in ["n","no"]:
            user_done = True

main()

    
