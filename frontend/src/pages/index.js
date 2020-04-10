import React, { useEffect, useState } from "react"
import { Link } from "gatsby"

import Layout from "../components/layout"
import Image from "../components/image"
import SEO from "../components/seo"
import PlayBoard from "../components/board"
import CrayonChooser from "../components/crayon"
import DemandCard from "../components/demandcard"


const IndexPage = () => {
  const [crayon, setCrayon] = useState(null)
  const [gameId, setGameId] = useState("0")
  const [money, setMoney] = useState(0)
  const [demandCards, setDemandCards] = useState([])
  const [inputMode, setInputMode] = useState("add_track")

  useEffect(() => {
    setGameId(new URLSearchParams(window.location.search).get("game_id"))
  })

  function adjustMoney() {
    return <div style={{ display: "inline-block", marginLeft: "5px" }}>
      <button onClick={() => {
        setMoney(money - 1)
      }} style={{ display: "inline-block" }}>- Money
      </button>
      <h3 style={{ display: "inline-block" }}>${money}</h3>
      <button onClick={() => {
        setMoney(money + 1)
      }} style={{ display: "inline-block" }}>+ Money
      </button>
    </div>
  }

  function drawDemand() {
    return <div style={{ display: "inline-block", marginLeft: "5px", marginRight: "5px" }}>
      <button onClick={() => {
        fetch(`/game/${gameId}/demand/random`).then(
          (response) => {
            return response.json()
          },
        ).then((data) => {
         setDemandCards(demandCards.concat([data.result]))
        })
      }}>Draw Demand Card</button>
    </div>
  }

  function makeDemandCards() {
    return <div>
      <h3>Demand Cards</h3>
      {demandCards.map((demandCard, index) => {
        return <DemandCard key={index} demands={demandCard.demands} removeMe={() => {
          setDemandCards((prevState => {
            const newState = []
            for (let i = 0; i < prevState.length; i++) {
              if (i !== index) {
                newState.push(prevState[i])
              }
            }
            return newState
          }))
        }}/>
      })}
    </div>
  }

  function moveTrain() {
    return inputMode === "add_track" ? <button onClick={() => {setInputMode("move_train")}}>Move Train</button> : <button onClick={() => {setInputMode("add_track")}}>Add Track</button>
  }

  return (
    <Layout>
      <SEO title="Home"/>
      <div>
        <CrayonChooser crayon={crayon} setCrayon={setCrayon}/>
        {adjustMoney()}
        {drawDemand()}
        {moveTrain()}
      </div>
      {makeDemandCards()}
      <PlayBoard gameId={gameId} crayon={crayon} inputMode={inputMode}/>
    </Layout>
  )
}

export default IndexPage
