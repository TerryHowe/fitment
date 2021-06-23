# Fitment
Copy ebay fitment from one listing to another.

It used to be if you found a listing on ebay autos that was the same as you wanted to sell, you could click "Sell one
like this" and it would copy most of the listing including fitment. Fitment now only gets copied if the auction you
use has an MPN or interchange number to provide fitment. This application uses the ebay api to copy the fitment from
one listing to another. You need to register in the ebay developers program and get a token.

I'm storing secrets in `.secrets.yml`, don't be like me.

    ebay_api_app_id: 'blah'
    ebay_auth_token: 'blech'

To run

    ./run.sh
