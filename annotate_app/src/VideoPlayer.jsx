import React, { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import NavbarComponent from "./NavbarComponent";
import ReactPlayer from "react-player";
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import FloatingLabel from 'react-bootstrap/FloatingLabel';
import { CSVLink, CSVDownload } from "react-csv";
import { LinkContainer } from "react-router-bootstrap";
import { useReactMediaRecorder } from "react-media-recorder";
import FileSaver from 'file-saver';
// import { ExportToCsv } from 'export-to-csv';


import vid0 from "./videos/videoMP4s/0.mp4";
import vid1 from "./videos/videoMP4s/1.mp4";
import vid2 from "./videos/videoMP4s/2.mp4";
import vid3 from "./videos/videoMP4s/3.mp4";
import vid4 from "./videos/videoMP4s/4.mp4";
import vid5 from "./videos/videoMP4s/5.mp4";
import vid6 from "./videos/videoMP4s/6.mp4";
import vid7 from "./videos/videoMP4s/7.mp4";
import vid8 from "./videos/videoMP4s/8.mp4";
import bits from "./assets/bits.png";

export default function VideoPlayer() {
  const location = useLocation();
  const { name, id } = location.state;
  const [currVideo, setCurrVideo] = useState(vid0);
  const [playing, setPlaying] = useState(true);
  const [playingID, setPlayingID] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [everythingDone, setEverythingDone] = useState(false);

  const canvasWidth = 300
  const canvasHeight = 300
  const jumpDistance = 10
  const LATENCYFORANNOTATIONINMS = 100
  
  const [form, setForm] = useState({
    valence: "",
    arousal: "",
    arousalValid: false,
    valenceValid: false,
  });

  const [locX, setLocX] = useState((canvasWidth/2)-0);
  const [locY, setLocY] = useState((canvasHeight/2)-0);

  const [val, setVal] = useState(5);
  const [aro, setAro] = useState(5);

  const [annotations, setAnnotations] = useState([["time,valence,arousal,videoID"]]);

  const { status, startRecording, stopRecording, mediaBlobUrl } =
    useReactMediaRecorder({ video: true, audio: true });


  const handleShow = () => {
    setShowModal(true);
    setPlaying(false); 
    setLocX((canvasWidth/2)-0)
    setLocY((canvasWidth/2)-0)
  }

  const handleSeek = (e) => {
    setPlaying(true);
    setShowModal(false);
    // setLocX((canvasWidth/2)-0)
    // setLocY((canvasWidth/2)-0)
  }

  // const orderedList =[vid5, vid0, vid3, vid0, vid7, vid0, vid8, vid0, vid1, vid0, vid2, vid0, vid4, vid0, vid6, vid0];
  const orderedList = [vid4, vid0, vid7, vid0, vid1, vid0, vid6, vid0, vid3, vid0, vid8, vid0, vid2, vid0, vid5, vid0];


  const handleVideoEnded = () => {
    
    if(playingID === orderedList.length - 1) {
      finishUp();
      
    }
    // comment below line if it breaks
    stopRecording()
    
    downloadVideo(mediaBlobUrl)

    // console.log("ENDED");
    setPlayingID((playingID + 1) % orderedList.length);

    console.log(orderedList[playingID])
    setCurrVideo(orderedList[playingID]);
    startRecording();
    setPlaying(true);
  }

 
  const finishUp = () => {
    setShowModal(false);
    setPlaying(false);

    setEverythingDone(true);

  }

  const getVideoID = (video) => {
    if(video === vid0) {
      return 0;
    }
    if(video === vid1) {
      return 1;
    }
    if(video === vid2) {
      return 2;
    }
    if(video === vid3) {
      return 3;
    }
    if(video === vid4) {
      return 4;
    }
    if(video === vid5) {
      return 5;
    }
    if(video === vid6) {
      return 6;
    }
    if(video === vid7) {
      return 7;
    }
    if(video === vid8) {
      return 8;
    }
  }



// update the annotations array every 100ms
  useEffect(() => {
    // setInterval(() => {
      if (playing) {
        // if (getVideoID(currVideo) != 0){

          setAnnotations((annotations) => [...annotations, [Date.now(), val , aro , getVideoID(currVideo)]]);
          
       
        // }
        
      }
     
    // }, LATENCYFORANNOTATIONINMS);

  }, [playing, val , aro , currVideo]);

    
    
// DEPRECATED CODE FOR FORM VALIDATION FOR OLD MODAL


// const handleClose = () => {
//   setShowModal(false);
//   setPlaying(true);
// }

  // const handleChange = (e) => {
  //   setForm({
  //     ...form,
  //     [e.target.name]: e.target.value,
  //   });
  // };

  // const checkInRange = (val) => {
  //   if (val >= 1 && val <= 9) {
  //     return true;
  //   }
  //   return false;
  // }
  // const handleSubmit = (e) => {
  //   if (checkInRange(form.valence) && checkInRange(form.arousal)) {
  //     setForm({
  //       ...form,
  //       valenceValid: true,
  //       arousalValid: true,
  //     });
      
  //     //console.log(form);

  //     //newAnnotation = [Date.now(), form.valence, form.arousal];
  //     let newAnnotation = [Date.now(), form.valence, form.arousal, `${getVideoID(currVideo)}`];
  //     setAnnotations([...annotations, newAnnotation]);

  //     handleClose();
  //   }
  //   else {
  //     if(!checkInRange(form.valence) && checkInRange(form.arousal)) {
  //       setForm({
  //         ...form,
  //         valenceValid: false,
  //         arousalValid: true,
  //       });
  //     }
  //     else if(checkInRange(form.valence) && !checkInRange(form.arousal)) {
  //       setForm({
  //         ...form,
  //         valenceValid: true,
  //         arousalValid: false,
  //       });
  //     }
  //     else {
  //       setForm({
  //         ...form,
  //         valenceValid: false,
  //         arousalValid: false,
  //       });
  //     }
  //   }
  // };


  const handleSubmitCSV = (e) => {
    // console.log(annotations);
    const csv = annotations.map(row => row.join(',')).join('\n');

    const csvData = new Blob([csv], { type: 'text/csv;charset=utf-8;' });

    FileSaver.saveAs(csvData, 'data.csv');

    
  }

  
    
   //download video from blob_url
   const downloadVideo = (blob_url) => {
    if (getVideoID(currVideo) == 0){
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = blob_url;
    a.download = "user_" + id + "video_"+ getVideoID(currVideo) +".mp4";
    document.body.appendChild(a);
    a.click();

    window.URL.revokeObjectURL(blob_url);
    }
  };
  
  


  const leftPressed = () => {
    console.log("left pressed");
    if(locX > jumpDistance) {
      setLocX(locX - jumpDistance);
    }
    else{
      setLocX(0);
    }
  }
  const rightPressed = () => {
    console.log("right pressed");
    if(locX < canvasWidth - jumpDistance) {
      setLocX(locX + jumpDistance);
    }
    else{
      setLocX(canvasWidth);
    }
  }
  const upPressed = () => {
    console.log("up pressed");
    if(locY > jumpDistance) {
      setLocY(locY - jumpDistance);
    }
    else{
      setLocY(0);
    }
  }
  const downPressed = () => {
    console.log("down pressed");
    if(locY < canvasHeight - jumpDistance) {
      setLocY(locY + jumpDistance);
    }
    else{
      setLocY(canvasHeight);
    }
  }

  const handleKeyDown = (e) => {
    e.preventDefault();
    if (e.key === "ArrowLeft") {
      leftPressed()
    }
    if (e.key === "ArrowRight") {
      rightPressed()
    }
    if (e.key === 'ArrowUp') {
      upPressed()
    }
    if (e.key === 'ArrowDown') {
      downPressed()
    }   
    
  };

  const canvasRef = useRef(null);
  const canvasRef2 = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    const canvas2 = canvasRef2.current;
    const context2 = canvas2.getContext("2d");
  }, []);

  const round = (value, decimals) => {
    return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
  }

  const getArou = (locX, locY) => {
    return round(8 - (locY / canvasWidth) * 8 + 1, 2);
  }

  const getVal = (locX, locY) => {
    return round((locX / canvasWidth) * 8 + 1, 2);
  }

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    context.beginPath();

    context.fillStyle = '#DDDDDD';
    context.fillRect(0, 0, canvas.width, canvas.height);

    context.clearRect(0, 0, canvas.width, canvas.height);
    
    context.beginPath();
    context.arc(locX, locY, 6, 0, 2 * Math.PI, false);
    context.fillStyle = 'red';
    context.fill();

    const canvas2 = canvasRef2.current;
    const context2 = canvas2.getContext("2d");

    let img = new Image();
    img.src = '/valArou.png';
    img.onload = function() {
      context2.drawImage(img, 0, 0, canvas.width, canvas.height);
    }

    setVal(getVal(locX, locY));
    setAro(getArou(locX, locY));

  }, [locX, locY]);

  
  

  //timer after every 30 seconds to show the modal
  // useEffect(() => {
  //   const interval = setInterval(() => {
  //     if(playing) {
  //       handleShow();
  //     }
  //   }, 30000);
  //   return () => clearInterval(interval);
  // }, [playing]);




  return (
    <>
      <Container onKeyDown={(e) => handleKeyDown(e)} tabIndex={0} style={{outline: "none" , transition: "1ms"}}>
        <NavbarComponent page="video" />
        <Row className="d-flex justify-content-center align-items-center">
          <Col md={8} lg={6} xs={12}>
            VIDEO PLAYER - User <b>{name}</b> ; PlayingID <b>{playingID}</b> ; Arousal - <b>{aro}</b> Valence - <b>{val}</b> ;
          </Col>
        </Row>
        <Row className="d-flex justify-content-center align-items-center">
          <Col md={10} lg={10} xs={12}>
            <ReactPlayer onSeek={handleSeek} onPause={handleShow} url={currVideo} playing={playing} controls light={bits} width={`85%`} height={`auto`} onEnded={handleVideoEnded} />
          </Col>
        </Row>


        <Row className="d-flex justify-content-center align-items-center">
        <div style={{ textAlign: 'left' }}>
          {/* <CSVLink data={annotations} filename={`${id}_annotation.csv`}> */}
            <Button variant="primary" onClick={handleSubmitCSV} style={{ width: '200px', fontSize: '16px' }}>
              Download CSV of Annotations 
            </Button>
          {/* </CSVLink> */}
          </div>
        </Row>
{/* Make div float at right top part of screen */}
        <Row className="d-flex justify-content-center align-items-center">
          <Col>
            <div style={{position: 'fixed', bottom:'480px', right: '300px'}}> 
              
              <canvas ref={canvasRef2} width={canvasWidth} height={canvasHeight} style={{position: 'absolute'}} />
              <canvas ref={canvasRef} width={canvasWidth} height={canvasHeight} style={{position: 'absolute'}} />
            
            </div>
          </Col>
          <Col>
            <div style={{margin: '1vw', padding: '1vw'}}>
              
            </div>
          </Col>
        </Row>

        <Row>
          <Col>
            {status}
            {(status === "idle" || status === "stopped") && <Button variant="primary" onClick={startRecording}>
              Start Recording
            </Button>}
            {status === "recording" && <Button variant="primary" onClick={stopRecording}>
              Stop Recording
            </Button>}
            {status === "stopped" && <Button variant="primary" onClick={() => downloadVideo(mediaBlobUrl)}>
              Download Video
             </Button>}
          </Col>
        </Row>
      </Container>
      {/* {!everythingDone && (<Modal show={showModal} onHide={handleClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>Annotate your Valence and Arousal</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <FloatingLabel className="mb-3" controlId="AnnotateForm.Valence" label="Valence (1 - 9)">
              <Form.Control type="text" name="valence" onChange={handleChange} value={form.valence} placeholder="1 - 10" isInvalid={!form.valenceValid} />
            </FloatingLabel>
            <FloatingLabel className="mb-3" controlId="AnnotateForm.Arousal" label="Arousal (1 - 9)">
              <Form.Control type="text" name="arousal" onChange={handleChange} value={form.arousal} placeholder="1 - 10" isInvalid={!form.arousalValid} />
            </FloatingLabel>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Close
          </Button>
          <Button variant="primary" onClick={handleSubmit}>
            Save Changes
          </Button>
        </Modal.Footer>
      </Modal>)}
      {everythingDone && (<Modal show={true} onHide={handleClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>All done!</Modal.Title>
        </Modal.Header>
        <Modal.Footer>
          {/* <LinkContainer to="/review" state={{ name: `${form.name}`, id: `${id}` }}> */}
          {/*  <Button variant="primary">
              Close
            </Button>
          {/* </LinkContainer> */}
        {/*</Modal.Footer>
      </Modal>)} */}
      
      {/* {everythingDone && <CSVDownload data={annotations} filename={`${id}_annotation.csv`} target="_blank" />} */}
    </>
  );
}
