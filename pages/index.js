// Main index page for the Next.js application
import { useState } from 'react';
import Head from 'next/head';

export default function Home() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Function to check API status
  const checkStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      setStatus(data);
    } catch (err) {
      setError('Failed to check API status: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <Head>
        <title>Social Media Automation</title>
        <meta name="description" content="Social Media Automation with TikTok Integration" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1 className="title">
          Social Media Automation
        </h1>

        <p className="description">
          TikTok API Integration
        </p>

        <div className="grid">
          <div className="card">
            <h2>API Status</h2>
            <button onClick={checkStatus} disabled={loading}>
              {loading ? 'Checking...' : 'Check Status'}
            </button>
            
            {error && (
              <div className="error">
                {error}
              </div>
            )}
            
            {status && (
              <div className="status">
                <pre>{JSON.stringify(status, null, 2)}</pre>
              </div>
            )}
          </div>

          <div className="card">
            <h2>API Endpoints</h2>
            <ul>
              <li><code>/api/status</code> - Check API status</li>
              <li><code>/api/tiktok/account</code> - Get TikTok account info</li>
              <li><code>/api/tiktok/post</code> - Post content to TikTok</li>
            </ul>
          </div>
        </div>
      </main>

      <footer>
        <p>
          Social Media Automation System
        </p>
      </footer>

      <style jsx>{`
        .container {
          min-height: 100vh;
          padding: 0 0.5rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
        }

        main {
          padding: 5rem 0;
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
        }

        footer {
          width: 100%;
          height: 100px;
          border-top: 1px solid #eaeaea;
          display: flex;
          justify-content: center;
          align-items: center;
        }

        a {
          color: #0070f3;
          text-decoration: none;
        }

        .title {
          margin: 0;
          line-height: 1.15;
          font-size: 4rem;
          text-align: center;
        }

        .description {
          text-align: center;
          line-height: 1.5;
          font-size: 1.5rem;
        }

        .grid {
          display: flex;
          align-items: center;
          justify-content: center;
          flex-wrap: wrap;
          max-width: 800px;
          margin-top: 3rem;
        }

        .card {
          margin: 1rem;
          flex-basis: 45%;
          padding: 1.5rem;
          text-align: left;
          color: inherit;
          text-decoration: none;
          border: 1px solid #eaeaea;
          border-radius: 10px;
          transition: color 0.15s ease, border-color 0.15s ease;
        }

        .card h2 {
          margin: 0 0 1rem 0;
          font-size: 1.5rem;
        }

        .card p {
          margin: 0;
          font-size: 1.25rem;
          line-height: 1.5;
        }

        button {
          background-color: #0070f3;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 5px;
          cursor: pointer;
          font-size: 1rem;
          margin-bottom: 1rem;
        }

        button:hover {
          background-color: #0051a2;
        }

        button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .error {
          color: red;
          margin-top: 1rem;
        }

        .status {
          margin-top: 1rem;
          background-color: #f0f0f0;
          padding: 1rem;
          border-radius: 5px;
          overflow: auto;
        }

        code {
          background: #fafafa;
          border-radius: 5px;
          padding: 0.25rem;
          font-size: 1.1rem;
          font-family: Menlo, Monaco, Lucida Console, Liberation Mono,
            DejaVu Sans Mono, Bitstream Vera Sans Mono, Courier New, monospace;
        }

        @media (max-width: 600px) {
          .grid {
            width: 100%;
            flex-direction: column;
          }
        }
      `}</style>

      <style jsx global>{`
        html,
        body {
          padding: 0;
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto,
            Oxygen, Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue,
            sans-serif;
        }

        * {
          box-sizing: border-box;
        }
      `}</style>
    </div>
  );
}
