import { gridToBoardPixelX, gridToBoardPixelY } from "./components/boardlayers/common"
import React from "react"

export const types = {
  MOVE_TRAIN: "move_train",
  PLAYER_JOINED: "player_joined",
  PLAYER_CHANGED_COLOR: "player_changed_color",
  ADD_MAJOR_CITY: "add_major_city",
  ADD_MEDIUM_CITY: "add_medium_city",
  ADD_SMALL_CITY: "add_small_city",
  ADD_TRACK: "add_track",
  ADJUST_MONEY: "adjust_money",
  DEMAND_DRAW: "demand_draw",
  DEMAND_DISCARDED: "demand_discarded",
  GOOD_PICKUP: "good_pickup",
  GOOD_DELIVERED: "good_delivered",
  ERASE_TRACK: "erase_track",
  START_TURN: "start_turn",
  START_GAME: "start_game",
}

export function ofType(actions, type) {
  return actions.filter((action) => action.type === type)
}

export function trainLocations(actions) {
  const locations = {}

  ofType(actions, types.MOVE_TRAIN).forEach((action) => {
    locations[action.data.playerId] = action.data.to
  })

  return locations
}

export function goodSuppliers(actions, good) {
  const suppliers = []

  ofType(actions, types.ADD_MAJOR_CITY).forEach(action => {
    const [x, y] = action.data.location
    action.data.available_goods.map(goodSupplied => {
      if (good === goodSupplied) {
        suppliers.unshift({ x: x, y: y })
      }
    })
  })

  ofType(actions, types.ADD_MEDIUM_CITY).forEach(action => {
    const [x, y] = action.data.location
    action.data.available_goods.map(goodSupplied => {
      if (good === goodSupplied) {
        suppliers.unshift({ x: x, y: y })
      }
    })
  })

  ofType(actions, types.ADD_SMALL_CITY).forEach(action => {
    const [x, y] = action.data.location
    action.data.available_goods.map(goodSupplied => {
      if (good === goodSupplied) {
        suppliers.unshift({ x: x, y: y })
      }
    })
  })

  return suppliers
}

export function currentPlayers(actions){
  const players = {}

  ofType(actions, types.PLAYER_JOINED).forEach((action) => {
    players[action.data.playerId] = {
      playOrder: action.data.playOrder,
      playerId: action.data.playerId,
      playerName: action.data.screenName
    }
  })

  ofType(actions, types.PLAYER_CHANGED_COLOR).forEach((action) => {
    players[action.data.playerId].color = action.data.newColor
  })

  return players
}

export function colorForPlayer(actions, playerId){
  const playerColors = {}
  Object.values(currentPlayers(actions)).forEach((player) => {
    playerColors[player.playerId] = player.color
  })
  return playerColors[playerId]
}

export function moneyForPlayer(actions, playerId){
  let sum = 0

  ofType(actions, types.ADJUST_MONEY)
    .filter(action => action.data.playerId === playerId)
    .forEach((action) => {
    sum += action.data.amount
  })

  return sum
}

export function cities(actions){
  return ofType(actions, types.ADD_MAJOR_CITY).concat(
    ofType(actions, types.ADD_MEDIUM_CITY).concat(
      ofType(actions, types.ADD_SMALL_CITY)))
}

export function citiesAtLocation(actions, location) {
  const [x, y] = location

  return cities(actions).filter(action => {
    return action.data.location[0] === x && action.data.location[1] === y
  })
}


export function demandCardsForPlayer(actions, playerId){
  const drawn = ofType(actions, types.DEMAND_DRAW)
    .filter(action => action.data.playerId === playerId)
    .map(action => {
      return { id: action.data.demandCardId, demands: action.data.demands }
    })

  const discardedIds = ofType(actions, types.DEMAND_DISCARDED)
    .filter(action => action.data.playerId === playerId)
    .map(action => action.data.demandCardId)

  return drawn.filter((card) => !discardedIds.includes(card.id))
}

export function cargoForPlayer(actions, playerId){
  const pickedUp = ofType(actions, types.GOOD_PICKUP)
    .filter(action => action.data.playerId === playerId)
    .map(action => {
      return { id: action.sequenceNumber, good: action.data.good }
    })

  const deliveredIds = ofType(actions, types.GOOD_DELIVERED)
    .filter(action => action.data.playerId === playerId)
    .map(action => action.data.pickupId)

  return pickedUp.filter((pickup) => !deliveredIds.includes(pickup.id))
}

export function demandsFillable(actions, playerId){
  const myTrainLocation = trainLocations(actions)[playerId]

  if(myTrainLocation === undefined){
    return []
  }

  const city = citiesAtLocation(actions, myTrainLocation)[0]

  if(city === undefined){
    return []
  }

  const goodsCarried = cargoForPlayer(actions, playerId)
    .map(pickup => pickup.good)

  if(goodsCarried.length === 0){
    return []
  }

  const fillable = []

  const cards = demandCardsForPlayer(actions, playerId)

  cards.forEach(card => {
    card.demands.forEach(demand => {
      if(goodsCarried.includes(demand.good)){
        if(city.data.name === demand.destination){
          fillable.push({card: card.id, demand: demand.id})
        }
      }
    })
  })

  return fillable
}

export function currentTurn(actions, playerId){
  let mostRecentStart = null

  ofType(actions, types.START_TURN)
    .forEach(action => {
      mostRecentStart = action
    })

  const players = currentPlayers(actions)

  if (mostRecentStart === null || Object.keys(players).length === 0){
    return {
      playOrder: 0,
      playerName: "",
      isYou: false
    }
  }

  return {
    playOrder: mostRecentStart.data.playOrder,
    playerName: "somebody",
    isYou: players[playerId].playOrder === mostRecentStart.data.playOrder
  }
}

export function gameIsStarted(actions) {
  return ofType(actions, types.START_GAME).length > 0
}

export function trainMovementThisTurn(actions) {
  let mostRecentStart = null

  ofType(actions, types.START_TURN)
    .forEach(action => {
      mostRecentStart = action
    })

  if (mostRecentStart === null) {
    return 0
  }

  let movement = 0

  ofType(actions, types.MOVE_TRAIN)
    .filter(action => action.sequenceNumber > mostRecentStart.sequenceNumber)
    .forEach(action => {
      movement += action.data.movementUsed;
    })

  return movement
}

export function trackBuiltThisTurn(actions) {
  let mostRecentStart = null

  ofType(actions, types.START_TURN)
    .forEach(action => {
      mostRecentStart = action
    })

  if (mostRecentStart === null) {
    return 0
  }

  let spent = 0

  ofType(actions, types.ADD_TRACK)
    .filter(action => action.sequenceNumber > mostRecentStart.sequenceNumber)
    .forEach(action => {
      spent += action.data.spent;
    })

  return spent
}