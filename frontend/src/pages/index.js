import React, { useEffect, useState } from "react"
import { graphql, useStaticQuery } from "gatsby"
import base64 from "react-native-base64"

import Layout from "../components/layout"
import PlayBoard from "../components/board"
import CrayonChooser from "../components/crayon"
import DemandCard from "../components/demandcard"
import HostingTools from "../components/hostingtools"
import { default as moji } from "../components/openmoji"
import * as gamestate from "../gamestate"


const IndexPage = () => {
  const data = useStaticQuery(graphql`
    query {
      goods:  allFile(filter: {relativeDirectory: {eq: "openmoji/openmoji-svg-black"}}) {
        edges {
          node {
            id
            name
            publicURL
          }
        }
      }
    }
  `)

  const goodsIcons = {}
  data.goods.edges.forEach((edge) => {
    goodsIcons[edge.node.name + ".svg"] = edge.node.publicURL
  })

  const goodsNames = {}
  moji.forEach((emoji) => {
    goodsNames[emoji.hexcode + ".svg"] = emoji.annotation
  })

  const [player, setPlayer] = useState({ playerNumber: -1, screenName: "", color: "#ccc" })
  const [players, setPlayers] = useState([])

  const [gameId, setGameId] = useState("0")
  const [inputMode, setInputMode] = useState("move_train")
  const [showHostingTools, setShowHostingTools] = useState(false)
  const [needToFetch, setNeedToFetch] = useState(true)
  const [needToFetchPlayers, setNeedToFetchPlayers] = useState(true)
  const [actions, setActions] = useState([])

  useEffect(() => {
    setGameId(new URLSearchParams(window.location.search).get("game_id"))
  })

  useEffect(() => {
      if (gameId !== "0" && needToFetchPlayers) {
        async function f() {
          const myJson = await (await fetch(`/game/${gameId}/slot/mine/`)).json()
          const allJson = await (await fetch(`/game/${gameId}/slots/`)).json()
          setPlayer(myJson.result)
          setPlayers(allJson.result)

          setNeedToFetchPlayers(false)
        }

        f()
      }
    }, [gameId, needToFetchPlayers],
  )

  useEffect(() => {
    if (needToFetch && gameId !== "0") {
      fetch(`/game/${gameId}/actions/`).then(
        (response) => {
          return response.json()
        },
      ).then((data) => {
        setActions(data.result)
        setNeedToFetch(false)
      })
    }
  }, [needToFetch, gameId])

  useEffect(() => {
    let interval = setInterval(() => {
      fetch(`/game/${gameId}/actions/last/`).then(
        (response) => {
          return response.json()
        },
      ).then((data) => {
        if (actions.length > 0 && data.result.sequenceNumber > actions[actions.length - 1].sequenceNumber) {
          setNeedToFetch(true)
        }
      })
    }, 300)
    return function() {
      clearInterval(interval)
    }
  })

  const money = actions.map((action) => {
    if (action.type === "adjust_money" && action.data.playerNumber === player.playerNumber) {
      return action.data.amount
    } else {
      return 0
    }
  }).reduce(((previousValue, currentValue) => (previousValue + currentValue)), 0)

  const demandsDrawn = actions.map((action) => {
    if (action.type === "demand_draw" && action.data.playerNumber === player.playerNumber) {
      return { id: action.data.demandCardId, demands: action.data.demands }
    } else {
      return null
    }
  }).filter((value) => value !== null)

  const demandsCompletedOrDiscarded = {}
  actions.map((action) => {
    if (action.type === "demand_completed" || action.type === "demand_discarded") {
      demandsCompletedOrDiscarded[action.data.demandCardId] = true
    }
  })

  const demandCards = demandsDrawn.filter((card) => !demandsCompletedOrDiscarded[card.id])

  const goodsCarriedObject = {}

  actions.filter(
    (action) => (action.type === "good_pickup" && action.data.playerNumber === player.playerNumber),
  ).forEach((action) => {
    const good = action.data.good
    goodsCarriedObject[good] = goodsCarriedObject[good] || 0
    goodsCarriedObject[good] += 1
  })

  actions.filter(
    (action) => (action.type === "good_delivered" && action.data.playerNumber === player.playerNumber),
  ).forEach((action) => {
    const good = action.data.good
    goodsCarriedObject[good] -= 1
  })

  const goodsCarried = []

  Object.keys(goodsCarriedObject).forEach((good) => {
    if (goodsCarriedObject[good] > 0) {
      for (let i = 0; i < goodsCarriedObject[good]; i++) {
        goodsCarried.unshift(good)
      }
    }
  })

  let myTrainLocation = gamestate.trainLocations(actions)[player.playerNumber]
  let goodsAtLocation = []
  let demandsFillableAtLocation = {}
  let dumpable = false

  if (myTrainLocation !== undefined) {
    const citiesAtLocation = actions.filter((action) => action.data.location && action.data.location[0] === myTrainLocation[0] && action.data.location[1] === myTrainLocation[1])
    if (citiesAtLocation.length > 0) {
      dumpable = true
    }
    goodsAtLocation = citiesAtLocation.flatMap((cityAction) => {
      return cityAction.data.available_goods || []
    })
    demandCards.forEach((demandCard) => {
      demandCard.demands.forEach((demand) => {
        citiesAtLocation.filter((city) => city.data.name === demand.destination).forEach((city) => {
          if (goodsCarried.includes(demand.good)) {
            demandsFillableAtLocation[demandCard.id] = { good: demand.good, city: demand.destination }
          }
        })
      })
    })
  }

  function adjustMoney() {
    return <div style={{ display: "inline-block", marginLeft: "5px" }}>
      <h3 style={{ display: "inline-block", marginBottom: "5px" }}>${money}M</h3>
    </div>
  }

  function drawDemand() {
    return <div style={{ display: "inline-block", marginLeft: "5px", marginRight: "5px" }}>
      <button onClick={() => {
        fetch(`/game/${gameId}/actions/demand/draw/`, { method: "POST" }).then(() => {
          setNeedToFetch(true)
        })
      }}>Draw Demand Card
      </button>
    </div>
  }

  function makeDemandCards() {
    return <div style={{ backgroundColor: "#ddd", padding: "5px" }}>
      <h4>Demand Cards</h4>
      {demandCards.map((demandCard, index) => {
        return <DemandCard key={index} card={demandCard} fillable={demandsFillableAtLocation} fillAction={(good) => {
          fetch(`/game/${gameId}/actions/good/deliver/${good}/card/${demandCard.id}/`, { method: "POST" }).then(() => {
            setNeedToFetch(true)
          })
        }
        }/>
      })}
    </div>
  }

  function moveTrain() {
    return <div style={{display: "inline", marginRight: "5px"}}>
      <button style={{display: "inline"}} disabled={inputMode === "move_train"} onClick={() => {
        setInputMode("move_train")
      }}>Move Train
      </button>
      <button style={{display: "inline"}} disabled={inputMode === "add_track"} onClick={() => {
        setInputMode("add_track")
      }}>Add Track
      </button>
    </div>
  }

  function toggleHostingTools() {
    return <button onClick={() => {
      setShowHostingTools(!showHostingTools)
    }}>Toggle Host Tools</button>
  }

  function hostingTools() {
    return <HostingTools gameId={gameId} show={showHostingTools}/>
  }

  function pickupGoods() {
    const goods = goodsAtLocation.map((value, index) => <div key={index} style={{ display: "inline-block" }}>
      <img style={{ display: "block", margin: "0 auto 0" }} width={40} src={goodsIcons[value]}/>
      <button style={{ display: "block" }} onClick={() => {
        fetch(`/game/${gameId}/actions/good/pickup/${value}/`, { method: "POST" }).then(() => {
          setNeedToFetch(true)
        })
      }}>Pickup
      </button>
    </div>)
    return goods.length === 0 ? <></> :
      <div style={{ backgroundColor: "#ddd", display: "inline-block", margin: "5px" }}>
        <div>
          {goods}
        </div>
      </div>
  }

  function trainCargo() {
    const goodsIndicators = goodsCarried.map((good, index) => {
      return <div key={index} style={{ display: "inline-block", margin: "3px" }}>
        <img style={{ display: "inline-block", margin: "0" }} width={60} src={goodsIcons[good]}/>
        {dumpable ? <button style={{ display: "block" }} onClick={() => {
          fetch(`/game/${gameId}/actions/good/dump/${good}/`, { method: "POST" }).then(() => {
            setNeedToFetch(true)
          })
        }
        }>Dump</button> : <></>}
      </div>
    })
    if (goodsIndicators.length === 0) {
      return <></>
    }

    return <div style={{ backgroundColor: "#ddd", display: "inline-block", margin: "5px 5px 5px 0" }}>
      <h4 style={{
        textAlign: "center",
        marginTop: "5px",
        marginBottom: "3px",
      }}>Cargo</h4>
      <div>
        {goodsIndicators}
      </div>
    </div>
  }

  return (
    <Layout>
      <PlayBoard actions={actions} setNeedToFetch={setNeedToFetch} gameId={gameId} players={players}
                 inputMode={inputMode}>
        <div style={{ zIndex: 1, position: "relative" }}>
          {hostingTools()}
          <div style={{ position: "fixed", bottom: "0%", backgroundColor: "#ddd", padding: "5px" }}>
            <CrayonChooser crayon={player.color} setCrayon={(color) => {
              fetch(`/game/${gameId}/slot/${player.playerNumber}/set-color/${base64.encode(color)}/`, { method: "POST" }).then(
                (response) => {
                  setNeedToFetchPlayers(true)
                },
              )
            }}/>
            {adjustMoney()}
            {drawDemand()}
            {moveTrain()}
            {toggleHostingTools()}
          </div>
          <div style={{ position: "fixed", bottom: "60px" }}>
            {trainCargo()}
            {pickupGoods()}
            {makeDemandCards()}
          </div>
        </div>
      </PlayBoard>
    </Layout>
  )
}

export default IndexPage
