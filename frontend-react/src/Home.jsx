import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './Home.css';
import logoMypyli from './assets/images/logo_mypyli.png';
import candidatImg from './assets/images/candidat.png';


const iconMap = {
  Nom: "fa-user",
  Prénom: "fa-user",
  Prenom: "fa-user",
  Email: "fa-envelope",
  Téléphone: "fa-phone",
  Telephone: "fa-phone",
  Adresse: "fa-location-dot",
  AdresseComplete: "fa-location-dot",
  Langue: "fa-language",
  language: "fa-language",
  experience: "fa-briefcase",
  Expérience: "fa-briefcase",
  education: "fa-graduation-cap",
  Ville: "fa-city",
  Diplôme: "fa-graduation-cap",
  Certification: "fa-certificate",
  softskills: "fa-handshake-angle",
  hardskills: "fa-gears",
  Projet: "fa-folder-open",
  Profil: "fa-id-badge",
  Hobby: "fa-heart",
};

const Home = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [fileNames, setFileNames] = useState([]);
  const [jobOffer, setJobOffer] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const [modalVisible, setModalVisible] = useState(false);
  const [modalData, setModalData] = useState(null);

  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    const validFiles = files.filter(f => f.type === 'application/pdf');

    if (validFiles.length === 0) {
      alert("Veuillez déposer uniquement des fichiers PDF.");
      return;
    }

    setUploadedFiles(validFiles);
    setFileNames(validFiles.map(f => `📄 ${f.name}`));
    setResults([]);
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    const validFiles = files.filter(f => f.type === 'application/pdf');

    if (validFiles.length === 0) {
      alert("Veuillez sélectionner un ou plusieurs fichiers PDF.");
      return;
    }

    setUploadedFiles(validFiles);
    setFileNames(validFiles.map(f => `📄 ${f.name}`));
    setResults([]);
  };

  const extractEntitiesFromCV = async (file) => {
    const formData = new FormData();
    formData.append("cvs", file);

    const response = await fetch("http://127.0.0.1:8000/cvparser/upload-cv/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Échec de l'extraction des entités du CV.");
    return await response.json();
  };

  const extractEntitiesFromOffer = async (text) => {
    const response = await fetch("http://127.0.0.1:8000/nerapp/extract-offre/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ offer: text }),
    });

    if (!response.ok) throw new Error("Échec de l'extraction de l'offre.");
    return await response.json();
  };

  const computeScore = async (cvEntities, offerEntities) => {
    const payload = {
      cv: [cvEntities],
      offer: Object.entries(offerEntities).map(([label, textArray]) => ({
        text: Array.isArray(textArray) ? textArray : [textArray],
        label: label,
      })),
    };

    const response = await fetch("http://127.0.0.1:8000/scoring1/match1/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error("Erreur lors du calcul du score.");
    const data = await response.json();
    return data.matching_score;
  };

  const handleAnalyze = async () => {
    if (uploadedFiles.length === 0) {
      alert("Merci d'ajouter au moins un CV.");
      return;
    }
    if (!jobOffer.trim()) {
      alert("Merci d'ajouter une offre d'emploi.");
      return;
    }

    setLoading(true);
    setResults([]);

    try {
      const offerEntities = await extractEntitiesFromOffer(jobOffer);

      const resultsArray = [];

      for (const file of uploadedFiles) {
        const cvEntitiesRaw = await extractEntitiesFromCV(file);
        const cvEntities = Array.isArray(cvEntitiesRaw) && cvEntitiesRaw.length > 0 ? cvEntitiesRaw[0] : {};

        const score = await computeScore(cvEntities, offerEntities);

        resultsArray.push({
          entities: cvEntities,
          score: Number(score),
        });
      }

      setResults(resultsArray);
    } catch (error) {
      console.error("Erreur lors de l'analyse :", error);
      alert("Une erreur est survenue lors de l'analyse.");
    } finally {
      setLoading(false);
    }
  };

  const openModal = (entities) => {
    setModalData(entities);
    setModalVisible(true);
  };

  const closeModal = () => {
    setModalVisible(false);
    setModalData(null);
  };

  const formatValue = (val) => {
    if (Array.isArray(val)) return val.join(', ');
    if (typeof val === 'object') return JSON.stringify(val);
    return val;
  };

  const Modal = ({ data, onClose }) => {
    if (!data) return null;

    return (
      <div
        style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.6)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1250,
          padding: 20,
        }}
        onClick={onClose}
      >
        <div
          onClick={e => e.stopPropagation()}
          style={{
            backgroundColor: '#fff',
            borderRadius: '10px',
            width: '100%',
            maxWidth: 1000,
            maxHeight: '80vh',
            overflowY: 'auto',
            boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
            position: 'relative',
            padding: '30px 40px 40px 40px',
            fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
          }}
        >
          <button
            onClick={onClose}
            style={{
              position: 'absolute',
              top: 15,
              right: 15,
              border: 'none',
              background: 'transparent',
              fontSize: 24,
              cursor: 'pointer',
              color: '#888',
              transition: 'color 0.2s',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = '#d33')}
            onMouseLeave={e => (e.currentTarget.style.color = '#888')}
            aria-label="Fermer la fenêtre"
          >
            <i className="fa-solid fa-xmark"></i>
          </button>

          <h3 style={{ marginBottom: 25, color: '#4a7c59' }} className=" text-center">
            Détails du candidat
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
            {Object.entries(data).map(([key, val]) => {
              const iconClass = iconMap[key] || "fa-info-circle";
              return (
                <div
                  key={key}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    backgroundColor: '#f5f9f7',
                    padding: '10px 15px',
                    borderRadius: 8,
                    boxShadow: 'inset 1px 1px 4px rgba(0,0,0,0.05)',
                  }}
                >
                  <i
                    className={`fa-solid ${iconClass}`}
                    style={{ color: '#5caf8e', width: 25, textAlign: 'center', marginRight: 15, fontSize: 18 }}
                    aria-hidden="true"
                  />
                  <strong style={{ minWidth: 110, color: '#2d4739' }}>{key} :</strong>
                  <span style={{ marginLeft: 8, color: '#3a3a3a', wordBreak: 'break-word' }}>
                    {formatValue(val)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      <header className="d-flex justify-content-between align-items-center shadow-sm px-4 py-3 bg-white">
        <img src={logoMypyli} alt="Logo Mypyli RH" style={{ height: '50px' }} />
      </header>

      <section className="hero-section py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-md-6">
              <h1 className="hero-title">Optimisez le recrutement avec Mypyli RH</h1>
              <p className="hero-subtitle">
                Analyse intelligente de CVs et offres d’emploi pour un matching précis, rapide et intelligent.
              </p>
            </div>
            <div className="col-md-6 text-center">
              <img src={candidatImg} alt="candidat" width="400" />
            </div>
          </div>
        </div>
      </section>

      <section className="py-5 bg-white">
        <div className="container">
          <h2 className="mb-4 text-center" style={{ fontSize: '2rem' }}>
            Analyse de Correspondance{' '}
            <span style={{ color: '#5caf8e', fontWeight: 'bold' }}>
              CV ↔ Offre
            </span>
          </h2>
          <div className="row justify-content-center">
            <div className="col-md-8">
              <div
                className="drop-zone mb-4"
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => document.getElementById('fileInput').click()}
                style={{ cursor: "pointer", border: "2px dashed #aaa", padding: "20px", textAlign: "center" }}
              >
                Glissez et déposez votre ou vos CVs ici (PDF)
                <div id="fileName" style={{ marginTop: '10px' }}>
                  {fileNames.map((name, idx) => (
                    <div key={idx}>{name}</div>
                  ))}
                </div>
              </div>

              <input
                type="file"
                id="fileInput"
                accept=".pdf"
                multiple
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />

              <div className="mb-3">
                <label htmlFor="jobOffer" className="form-label">Offre d'emploi</label>
                <textarea
                  className="form-control"
                  id="jobOffer"
                  rows="6"
                  placeholder="Collez ici l'offre d'emploi..."
                  value={jobOffer}
                  onChange={(e) => setJobOffer(e.target.value)}
                />
              </div>

              <div className="d-grid">
                <button onClick={handleAnalyze} className="btn btn1" disabled={loading}>
                  {loading ? "Analyse en cours..." : "Analyser"}
                </button>
              </div>
            </div>

            <div style={{ marginTop: '20px' }}></div>
            <hr style={{ borderTop: '1.5px solid #ccc', margin: '10px 0 30px 0' }} />
            <div>
              {results.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-center mb-4" style={{ fontSize: '2rem' }}>
                    Résultats du <span style={{ color: '#5caf8e' }}>matching</span>
                  </h4>
                  <ul className="list-group">
                    {results.map((r, idx) => {
                      const prenom = r.entities["Prénom"] || r.entities["Prenom"] || "Prénom Inconnu";
                      const nom = r.entities["Nom"] || r.entities["nom"] || "Nom Inconnu";

                      const badgeClass = r.score < 50 ? "bg-danger" : "bg-success";

                      return (
                        <li
                          key={idx}
                          className="list-group-item d-flex justify-content-between align-items-center"
                        >
                          <div>
                            {prenom} {nom}
                          </div>
                          <div className="d-flex align-items-center gap-2">
                            <span className={`badge rounded-pill ${badgeClass}`}>
                              {r.score ? `${r.score.toFixed(2)} %` : "Score non dispo"}
                            </span>
                            <button
                               className="btn btn-sm btn-outline-green"
                              onClick={() => openModal(r.entities)}
                            >
                              Voir plus
                            </button>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
      {modalVisible && <Modal data={modalData} onClose={closeModal} />}
    </div>
  );
};

export default Home;
