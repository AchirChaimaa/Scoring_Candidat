import React from 'react';

const CandidateModal = ({ show, onClose, candidate }) => {
  if (!show || !candidate) return null;

  return (
    <div
      className="modal fade show"
      style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}
    >
      <div className="modal-dialog modal-lg">
        <div className="modal-content border-0 shadow-lg rounded-4">
          <div
            className="modal-header"
            style={{ backgroundColor: '#5caf8e', color: 'white' }}
          >
            <h5 className="modal-title">
              {candidate.entities["Prénom"] || candidate.entities["Prenom"]}{" "}
              {candidate.entities["Nom"] || candidate.entities["nom"]}
            </h5>
            <button
              type="button"
              className="btn-close btn-close-white"
              onClick={onClose}
            ></button>
          </div>
          <div className="modal-body">
            <table className="table table-striped table-hover">
              <tbody>
                {Object.entries(candidate.entities).map(([key, value], idx) => (
                  <tr key={idx}>
                    <th className="text-capitalize">{key}</th>
                    <td>{Array.isArray(value) ? value.join(", ") : value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="modal-footer">
            <button
              className="btn"
              style={{ backgroundColor: '#5caf8e', color: 'white' }}
              onClick={onClose}
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateModal;
