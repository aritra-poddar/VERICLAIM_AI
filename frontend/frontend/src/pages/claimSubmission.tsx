<div className="claim-eligibility-check">
  <div className="claim-form-container">
    <h2>VeriClaim: Insurance Claim Eligibility Check</h2>

    <table className="claim-form-table">
      <tbody>
        <tr>
          <td colSpan={2}>
            <label>Incident Description (User Query):</label>
            <textarea placeholder="I had a road accident two days ago and was hospitalized for 3 weeks."></textarea>
          </td>
        </tr>

        <tr>
          <td>
            <label>Requested Claim Amount ($):</label>
            <input type="number" placeholder="Enter claim amount" value="199" />
          </td>
          <td>
            <label>Patient Age:</label>
            <input type="number" placeholder="Enter age" value="21" />
          </td>
        </tr>

        <tr>
          <td>
            <label>Number of Previous Claims:</label>
            <input type="number" placeholder="Enter number" value="1" />
          </td>
          <td></td>
        </tr>
      </tbody>
    </table>

    <button className="verify-claim-button">Verify Claim Eligibility</button>

    {/* Example static review section */}
    <div className="review-section">
      <h3>Requires Review</h3>
      <ul>
        <li>Initial data received.</li>
        <li>Relevant Policy Clause P1: National Insurance Co. Ltd.</li>
        <li>Claim requires manual verification by policy team.</li>
      </ul>
    </div>
  </div>
</div> 