from app import create_app

if __name__ == '__main__':
    main_app = create_app()
    main_app.run('0.0.0.0', port=3002)
