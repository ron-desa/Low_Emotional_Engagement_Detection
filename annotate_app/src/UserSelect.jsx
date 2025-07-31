import { useState } from "react";
import "./UserSelect.css";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import NavbarComponent from "./NavbarComponent";
import Card from "react-bootstrap/Card";
import { LinkContainer } from "react-router-bootstrap";

function UserSelect() {
  const [form, setForm] = useState({
    name: "",
    id: "",
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    console.log(form);
  };

  return (
    <Container>
      <NavbarComponent page="root" />
      <Row className="d-flex justify-content-center align-items-center userSelect">
        <Col md={8} lg={6} xs={12}>
          <Card className="shadow">
            <Card.Body>
              <div className="mb-3 mt-md-4">
                <h2 className="fw-bold mb-2 text-uppercase ">
                  Enter your details
                </h2>
                <p className=" mb-5">Please enter your name and ID!</p>
                <div className="mb-3">
                  <Form>
                    <Form.Group className="mb-3" controlId="formBasicText">
                      <Form.Label className="text-center">Name</Form.Label>
                      <Form.Control
                        type="name"
                        name="name"
                        onChange={handleChange}
                        value={form.name}
                        placeholder="Enter your name"
                      />
                    </Form.Group>

                    <Form.Group className="mb-3" controlId="formBasicText">
                      <Form.Label>ID</Form.Label>
                      <Form.Control
                        type="id"
                        name="id"
                        onChange={handleChange}
                        value={form.id}
                        placeholder="Enter your ID"
                      />
                    </Form.Group>

                    <div className="d-grid">
                      <LinkContainer
                        to="/video"
                        state={{ name: `${form.name}`, id: `${form.id}` }}
                      >
                        <Button variant="primary" onClick={handleSubmit}>
                          Submit
                        </Button>
                      </LinkContainer>
                    </div>
                  </Form>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default UserSelect;
