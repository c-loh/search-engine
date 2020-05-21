# imports and set-up
from flask import Flask, redirect, url_for, render_template, request
app = Flask(__name__)
import search

# home page: prompt user for query and let them submit
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        # get whatever's entered in the "query" field of the html file
        userQuery = request.form["query"]
        # redirect to search results page
        return redirect(url_for("searcher", query=userQuery))
    else:
        # get whatever's entered in the "query" field of the html file
        userQuery = request.args.get("query")
        # redirect to search results page
        return redirect(url_for("searcher", query=userQuery))

# results page: take user-entered query and perform search on it
# call search function somehow?
@app.route("/searcher/<query>")
def searcher(query):
    # can use templates to write html code that depends on arguments
    # template html files have to be in templates folder !!!
    tuple_search = search.run(query)
    return render_template("results.html", query=query, results=tuple_search[0], seconds=tuple_search[1])
 
if __name__ == "__main__":
    # to run: run this module to get server started
    #         open home.html in browser
    #         ta daaaa
    app.run()







# from flask import Flask, render_template, request

# app = Flask(__name__)

# @app.route("/", methods=["GET", "POST"])
# def home():
#     # query = request.form['search']
#     # print(query)
#     return render_template("home.html")

# @app.route("/results", methods=['POST'])
# def results():
#     query = request.form['search']
#     # print(query)
#     return 'results: %s <br/> <a href="/">Back Home</a>' % (query)
#     # return render_template("results.html")

# if __name__ == "__main__":
#     print("bears")
#     app.run()