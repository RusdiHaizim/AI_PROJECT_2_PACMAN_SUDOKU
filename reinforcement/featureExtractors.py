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

def closestCapsule(pos, cap, walls):
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a cap at this location then exit
        if (pos_x, pos_y) in cap:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no cap found
    return None

def closestGhost(pos, ghosts, walls):
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a ghost at this location then exit
        for g in ghosts:
            if (pos_x, pos_y) == getInt(g.getPosition()):
                return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no ghost found
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
        features["#-of-ghosts-1-step-away"] = sum(
            (next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

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

def getInt(pos):
    x, y = pos
    intForm = (int(x), int(y))
    return intForm

class NewExtractor(FeatureExtractor):
    """
    Design you own feature extractor here. You may define other helper functions you find necessary.
    """
    startFlag = True
    ghostStart = []

    def getFeatures(self, state, action):

        "*** YOUR CODE HERE ***"
        food = state.getFood()
        walls = state.getWalls()
        scaredGhost = []
        activeGhost = []
        features = util.Counter()
        caps = state.getCapsules()
        minMovesGhost = 40  # This is the SCARED_TIMER of ghosts (40 moves before runs out)

        for ghost in state.getGhostStates():
            if not ghost.scaredTimer:
                activeGhost.append(ghost)
            else:
                scaredGhost.append(ghost)
                if ghost.scaredTimer < minMovesGhost:
                    minMovesGhost = ghost.scaredTimer

        if self.startFlag:
            self.startFlag = False
            for g in activeGhost:
                self.ghostStart.append(getInt(g.getPosition()))

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)
        nextPos = (next_x, next_y)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum(
            nextPos in Actions.getLegalNeighbors(getInt(g.getPosition()), walls) for g in activeGhost)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood(nextPos, food, walls)
        distC = closestCapsule(nextPos, caps, walls)

        if distC is not None and len(activeGhost) > len(scaredGhost):
            cc = float(distC) / (walls.width * walls.height)
            cf = float('inf')
            if dist is not None:
                cf = float(dist) / (walls.width * walls.height)
            features["closest-cap"] = cc
            if cc <= cf:
                features["closest-food"] = 0.0
            else:
                features["closest-food"] = cf
        else:
            features["closest-food"] = float(dist) / (walls.width * walls.height)

        # if caps:
        #     distCapsule = closestCapsule(nextPos, caps, walls)
        #     if distCapsule is not None:
        #         features["closest-capsule"] = float(distCapsule) / (walls.width * walls.height)
        # else:
        #     dist = closestFood((next_x, next_y), food, walls)
        #     if dist is not None:
        #         # make the distance a number less than one otherwise the update
        #         # will diverge wildly
        #         features["closest-food"] = float(dist) / (walls.width * walls.height)
        #         if food[next_x][next_y]:
        #             features["eats-food"] = 1.0

        # Pursue ghosts in self-defence (omnivore pacman, vegans pls don't flame pl0x)
        # if len(scaredGhost) > 0:
        #     distG = closestGhost(nextPos, scaredGhost, walls)
        #     # Only eat ghost if pacman can catch up to scaredGhost in time, and there's
        #     # no incoming activeGhosts
        #     if distG is not None and distG < minMovesGhost:
        #         cg = float(distG) / (walls.width * walls.height)
        #         if cg < features["closest-food"]:
        #             for g in scaredGhost:
        #                 if nextPos == getInt(g.getPosition()):
        #                     features["eats-ghost"] = 1.0
        #             features["closest-ghost"] = cg
        #             features["closest-food"] = 0
        #             features["closest-capsule"] = 0
        notTrap = True
        for g in scaredGhost:
            if nextPos == getInt(g.getPosition()) and nextPos in self.ghostStart:
                notTrap = False
                break

        if len(scaredGhost) > 0 and notTrap:
            distG = closestGhost(nextPos, scaredGhost, walls)
            # Only eat ghost if pacman can catch up to scaredGhost in time, and there's
            # no incoming activeGhosts
            if distG is not None and distG < minMovesGhost:
                cg = float(distG) / (walls.width * walls.height)
                features["closest-ghost"] = cg
                for g in scaredGhost:
                    if nextPos == getInt(g.getPosition()):
                        features["eats-ghost"] = 1.0
                features["closest-food"] = 0
                features["closest-capsule"] = 0

        # if len(scaredGhost) > 0:
        #     distScaredGhost = closestGhost(nextPos, scaredGhost, walls)
        #     if distScaredGhost is not None:
        #         features["closest-scared-ghost"] = float(distScaredGhost) / (walls.width * walls.height)
        #     for g in scaredGhost:
        #         if nextPos == getInt(g.getPosition()):
        #             features["eat-scared-ghost"] = 1.0
        #     features["closest-food"] = 0
        #     features["closest-capsule"] = 0

        features.divideAll(10.0)
        return features