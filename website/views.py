from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from sqlalchemy import desc

views = Blueprint("views", __name__)

@views.route("/", methods=['GET'], defaults={"page": 1}) 
@views.route("/home", methods=['GET'], defaults={"page": 1})
@views.route('/home/<int:page>',methods=['GET'])
def home(page):
    page=page
    per_page = 10
    posts = db.session.query(Post).order_by(desc(Post.like_num)).paginate(page,per_page,error_out=False)


    return render_template("home.html", user = current_user, posts=posts)


@views.route("/create-post", methods = ['GET','POST'])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title cannot be empty!', category='error')
        elif not content:
            flash('Topic cannot be empty!', category='error')
        else:
            post = Post(title=title, content=content, author = current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('New topic created!', category = 'success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash('Post does not exist', category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Successfully deleted!', category='success')

    
    return redirect(url_for('views.home'))

@views.route("/posts/<username>",methods=['GET'], defaults={"page": 1})
@views.route("/posts/<username>/<int:page>",methods=['GET'])
@login_required
def posts(username, page):
    user = User.query.filter_by(username=username).first()
    page=page
    per_page = 4
    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = Post.query.filter_by(author=user.id).order_by(desc(Post.date_created)).paginate(page,per_page,error_out=False)

    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/edit-post/<id>", methods=['GET','POST'])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first()
    if request.method == "POST":
        post.title = request.form['title']
        post.content = request.form['content']
        if not post.title:
            flash('Title is required!', category='error')
        elif not post.content:
            flash('Content is required!', category='error')
        else:   
            post.update=Post(title=post.title,content=post.content,author = current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Topic has been updated!', category='success')
            return redirect(url_for('views.home'))

    return render_template('edit_post.html', user=current_user)

@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty!', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))
    
@views.route("/like-post/<post_id>", methods=['GET'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        flash('Topic does not exist!', category='error')
    elif like:
        post.like_num = post.like_num - 1
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        post.like_num = post.like_num + 1
        db.session.add(like)
        db.session.commit()

    return redirect(url_for('views.home'))
