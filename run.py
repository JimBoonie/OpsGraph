from app import app

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, 
                        help='Port to access application')
    args = parser.parse_args()

    app.run(debug=True, port=args.port)