import base64 from "react-native-base64"

export function advanceTurn(gameId) {
  fetch(`/game/${gameId}/actions/flow/advance/turn/`, { method: "POST" })
}

export function fetchMovementDestinations(gameId, setDestinations) {
  fetch(`/game/${gameId}/networks/train/destinations/`)
    .then(response => response.json())
    .then(data => {setDestinations(data.result)})
}


export function fetchMyPlayerId(gameId, setMyPlayerId) {
  fetch(`/game/${gameId}/my-player-id/`).then(
    (response) => {
      return response.json()
    },
  ).then((data) => {
    setMyPlayerId(data.result)
  })
}

export function fetchAllActions(gameId, setActions){
  fetch(`/game/${gameId}/actions/`).then(
    (response) => {
      return response.json()
    },
  ).then((data) => {
    setActions(data.result)
  })
}

export function fetchSupplementalActions(gameId, actions, setActions){
  const lastLocalSequenceNumber = Math.max(...actions.map(action => action.sequenceNumber))
  fetch(`/game/${gameId}/actions/after/${lastLocalSequenceNumber}/`).then(
    (response) => {
      return response.json()
    },
  ).then((data) => {
    if(data.result.length > 0) {
      setActions(actions.concat(data.result))
    }
  })
}

export function createInviteCode(gameId, setJoincode){
  fetch(`/game/${gameId}/invite/create/`, {method: "POST"})
    .then(response => response.json())
    .then(data => {
      setJoincode(data.result.invite)
    })
}

export function adjustMoney(gameId, playerId, amount){
  fetch(`/game/${gameId}/actions/adjust-money/player/${playerId}/${amount > 0 ? "plus" : "minus"}/${Math.abs(amount)}/`, { method: "POST" })
}

export function drawDemandCard(gameId) {
  fetch(`/game/${gameId}/actions/demand/draw/`, { method: "POST" })
}

export function setMyColor(gameId, playerId, color){
  fetch(`/game/${gameId}/slot/${playerId}/set-color/${base64.encode(color)}/`, { method: "POST" })
}

export function startGame(gameId){
  fetch(`/game/${gameId}/actions/flow/start/`, { method: "POST" })
}