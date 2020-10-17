import React from "react";
import * as gamestate from "../../gamestate";


const PlayerDisplay = (props) => {
    const actions = props.actions;

    const players = Object.values(gamestate.currentPlayers(actions))
    players.sort(p => p.playOrder)

    const playersHtml = players.map((player, index) => {
        return <div style={{
            display: "inline"
        }}
                    key={index}>
            <p style={{
                display: "inline",
                marginRight: "30px"
            }}>
                <div style={{
                    display: "inline-block",
                    backgroundColor: player.color,
                    width: "20px",
                    height: "20px",
                    marginTop: "5px",
                    marginBottom: "-2px",
                    marginRight: "5px",
                }}/>
                {player.playerName}</p>
        </div>
    })

    return (
        <div style={{backgroundColor: "#ddd"}}>
            <h5 style={{display: "inline", marginRight:"10px"}}>Players</h5>
            {playersHtml}
        </div>
    )
}

export default PlayerDisplay