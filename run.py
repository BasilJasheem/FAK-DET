from flaskblog import app

if __name__ == '__main__':
    app.run(debug=True)



@app.route("/detail/<item>", methods=['GET', 'POST'])
def detail(item):
    form = ReviewfillForm()
    item1 = item
    session['item']=item
        
    
    if 'item' in session:
        product_1 = Product.query.filter_by(id = item).first()
        item = session['item']
        review = Review.query.filter_by(item_id = item).all()
        username = current_user.username
        
        if request.method == 'POST':
            rev_text = request.form['review']
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            rev_1 = Review(rev_name =username, item_id =item, rev_text =rev_text, staus =0, rate =7.0, mark =0, ip =ip_address, i_mark =1, i_ignore =0)
            db.session.add(rev_1)
            db.session.commit()
            flash('Your review has been provided!', 'success')
            return redirect(url_for('detail', item = item))
        return render_template('detail.html', title='Product', item=item, product=product_1, form=form, review=review)
    return render_template('detail.html', title='About')