# Python Fast API endpoints For ticketing
An implementation for API endpoints that:
<ol>
<li>Save the ticket outputs to MongoDB</li>
<li>Retrieve the output from the database (batch and a single record by id)</li>
<li>Updates the record in the database</li>
  </ol>
  
## Endpoints
<table>
  <tr>
    <th>Functionality</th>
    <th>Method</th>
    <th>Endpoint</th>
  </tr>
  <tr>
    <td>Save the ticket outputs to MongoDB</td>
    <td>POST</td>
    <td>/Excel2json</td>
  </tr>
  <tr>
    <td>Retrieve All the Database Records</td>
    <td>GET</td>
    <td>/ticketsByBatch</td>
  </tr>
  <tr>
    <td>Retrieve Database Records By ID.</td>
    <td>GET</td>
    <td>/ticketsByBatchById</td>
  </tr>
  <tr>
    <td>Updates the Record in the Database.</td>
    <td>PUT</td>
    <td>/update_ticket</td>
  </tr>
  
</table>

## Testing the Endepoints Locally
1. This program was developed Using Pycharm
2. Check for the project dependencies :requirements.txt
3. Run the app.py

