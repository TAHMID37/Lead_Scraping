import React from 'react';
import './JobDetail.css';

function JobDetail({ job, onClose }) {
  if (!job) return null;

  return (
    <div className="job-detail-overlay" onClick={onClose}>
      <div className="job-detail-modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>&times;</button>
        
        <div className="job-detail-content">
          <h2>{job.job_title}</h2>
          
          <div className="detail-section">
            <h3>Company</h3>
            <p className="company-name">{job.employer_name}</p>
          </div>

          <div className="detail-section">
            <h3>Location</h3>
            <p>{job.location}</p>
          </div>

          {job.posted_date && job.posted_date !== 'Unknown' && (
            <div className="detail-section">
              <h3>Posted Date</h3>
              <p>{job.posted_date}</p>
            </div>
          )}

          <div className="detail-section">
            <h3>Job Description</h3>
            <p className="job-description">{job.job_description}</p>
          </div>

          {job.anzsco_assessment && (
            <div className="detail-section anzsco-section">
              <h3>ANZSCO 482 Assessment</h3>
              
              <div className="assessment-grid">
                <div className="assessment-item">
                  <strong>Eligibility:</strong>
                  <span className={`eligibility-badge ${job.anzsco_assessment.eligible ? 'eligible' : 'not-eligible'}`}>
                    {job.anzsco_assessment.eligible ? '✓ Eligible' : '✗ Not Eligible'}
                  </span>
                </div>

                {job.anzsco_assessment.occupation && (
                  <div className="assessment-item">
                    <strong>Occupation:</strong>
                    <span>{job.anzsco_assessment.occupation}</span>
                  </div>
                )}

                {job.anzsco_assessment.anzsco_code && (
                  <div className="assessment-item">
                    <strong>ANZSCO Code:</strong>
                    <span>{job.anzsco_assessment.anzsco_code}</span>
                  </div>
                )}

                {job.anzsco_assessment.confidence_score !== undefined && (
                  <div className="assessment-item">
                    <strong>Confidence Score:</strong>
                    <span>{(job.anzsco_assessment.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                )}
              </div>

              {job.anzsco_assessment.reason && (
                <div className="assessment-reason">
                  <strong>Assessment Reason:</strong>
                  <p>{job.anzsco_assessment.reason}</p>
                </div>
              )}
            </div>
          )}

          {job.url && (
            <div className="detail-section">
              <a href={job.url} target="_blank" rel="noopener noreferrer" className="apply-button">
                View Original Job Posting →
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default JobDetail;
