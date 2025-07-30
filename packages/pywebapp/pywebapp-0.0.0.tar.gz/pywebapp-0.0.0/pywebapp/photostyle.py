

if __name__ == "__main__":
    import os
    os.environ["PHOTOSTYLE_ENV"] = "prod"
    
    from main import main
    main()