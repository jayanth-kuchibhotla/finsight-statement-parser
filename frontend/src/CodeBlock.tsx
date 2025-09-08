import React from 'react';
import './assets/css/CodeBlock.css';

const CodeBlock: React.FC = () => {
  return (
    <div className="code-block-section section">
      <div className="container">
        <h2>Easy to Integrate</h2>
        <p>Our API is designed to be simple and intuitive. Here's a quick example of how to upload a statement using our Python library:</p>
        <div className="code-block">
          <pre>
            <code>
              <span className="comment"># Install our library</span>
              <br />
              <span className="keyword">pip install</span> fintech-sdk
              <br />
              <br />
              <span className="comment"># Import and configure</span>
              <br />
              <span className="keyword">from</span> fintech <span className="keyword">import</span> Client
              <br />
              <br />
              client = Client(api_key="YOUR_API_KEY")
              <br />
              <br />
              <span className="comment"># Upload a statement</span>
              <br />
              <span className="function">client.statements.upload</span>(
              <br />
              {'  '}file_path="/path/to/your/statement.pdf"
              <br />
              )
            </code>
          </pre>
        </div>
      </div>
    </div>
  );
};

export default CodeBlock;
