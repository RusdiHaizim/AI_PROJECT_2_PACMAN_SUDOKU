# featureExtractors.py
# --------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"Feature extractors for Pacman game states"

from game import Directions, Actions
import util

class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state,action)] = 1.0
        return feats

class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats

def closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """

    def getFeatures(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)
        features.divideAll(10.0)
        return features

        
        

class NewExtractor(FeatureExtractor):
    """
    Design you own feature extractor here. You may define other helper functions you find necessary.
    """
    def getFeatures(self, state, action):
        "*** YOUR CODE HERE ***"
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()
        scaredGhost = []
        activeGhost = []
        features = util.Counter()
        features["capsules"] = len(state.getCapsules())
        minMovesGhost = 40 # This is the SCARED_TIMER of ghosts (40 moves before runs out)
        
        for ghost in state.getGhostStates():
            if not ghost.scaredTimer:
                activeGhost.append(ghost)
            else:
                scaredGhost.append(ghost)
                if ghost.scaredTimer < minMovesGhost:
                    minMovesGhost = ghost.scaredTimer

        # Return remapped list containing manhattan distances btw ghost and pacman
        pos = state.getPacmanPosition()
        def getManhattanDistances(ghosts): 
            return map(lambda g: util.manhattanDistance(pos, g.getPosition()), ghosts) 
                    
        distanceToClosestActiveGhost = distanceToClosestScaredGhost = 0
        
        features["bias"] = 1.0
        
        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)
        u_x, u_y = next_x, next_y + 1
        d_x, d_y = next_x, next_y - 1
        l_x, l_y = next_x - 1, next_y
        r_x, r_y = next_x + 1, next_y
        
        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
        
        features["#-of-ghosts-2-step-away"] += sum((u_x, u_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
        features["#-of-ghosts-2-step-away"] += sum((d_x, d_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
        features["#-of-ghosts-2-step-away"] += sum((l_x, l_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
        features["#-of-ghosts-2-step-away"] += sum((r_x, r_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-2-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
          # make the distance a number less than one otherwise the update
          # will diverge wildly
          features["closest-food"] = float(dist) / (walls.width * walls.height)

        # Pursue ghosts in self-defence (omnivore pacman, vegans pls don't flame pl0x)
        if scaredGhost:
            distanceToClosestScaredGhost = min(getManhattanDistances(scaredGhost))
            if activeGhost:
                distanceToClosestActiveGhost = min(getManhattanDistances(activeGhost))
            else:
                distanceToClosestActiveGhost = 10
            # Only eat ghost if pacman can catch up toe scaredGhost in time, and there's
            # no incoming activeGhosts
            if distanceToClosestScaredGhost < minMovesGhost/2 - 1 and distanceToClosestActiveGhost > 3:
                #print distanceToClosestScaredGhost, distanceToClosestActiveGhost, minMovesGhost
                features["#-of-ghosts-1-step-away"] = 0.0
                features["#-of-ghosts-2-step-away"] = 0.0
                features["eats-food"] = 0.0
                
        features.divideAll(10.0)
        return features


        
