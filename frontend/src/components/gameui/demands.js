import React from "react"
import DemandCard from "./demandcard"
import * as gamestate from "../../gamestate"

const DemandCards = (props) => {
  const actions = props.actions
  const playerId = props.playerId
  const gameId = props.gameId

  const demandCards = gamestate.demandCardsForPlayer(actions, playerId)
  const fillable = gamestate.demandsFillable(actions, playerId)

  return <div style={{ backgroundColor: "#ddd", padding: "5px" }}>
    <h4>Demand Cards</h4>
    {demandCards.map((demandCard, index) => {
      return <DemandCard key={index} card={demandCard} fillable={fillable} fillAction={(good) => {
          fetch(`/game/${gameId}/actions/good/deliver/${good}/card/${demandCard.id}/`, { method: "POST" })
        }
      }/>
    })}
  </div>
}

export default DemandCards