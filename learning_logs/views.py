from django.shortcuts import render
from .models import Topic,Entry
from django.http import HttpResponseRedirect,Http404
from django.urls import reverse
from .forms import TopicForm,EntryForm
from django.contrib.auth.decorators import login_required

# Create your views here.


def index(request):
    '''学习笔记的主页'''
    return render(request,'learning_logs/index.html')

@login_required
def topics(request):
    '''显示所有的主题'''
    # pylint: disable=no-member
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    #下面这个注释是为了解决关于*[pylint]E1101:Module 'xxx' has no 'xxx' member* 简单而有效的解决办法  加上就可以解决
    # pylint: disable=no-member
    #topics = Topic.objects.order_by('date_added')
    context = {'topics':topics}
    return render(request,'learning_logs/topics.html',context)

@login_required
def topic(request,topic_id):
    ''' 显示单个主题及其所有的条目 '''
    #pylint: disable=no-member
    topic = Topic.objects.get(id=topic_id)
    #确定请求的主题属于当前用户
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic':topic,'entries':entries}
    return render(request,'learning_logs/topic.html',context)

@login_required
def new_topic(request):
    if request.method != 'POST':
        #未提交数据，创建一个新表单
        form = TopicForm()
    else:
        #post提交的数据，对数据进行处理
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            #form.save()
            return HttpResponseRedirect(reverse('learning_logs:topics'))
    context = {'form':form}
    return render(request,'learning_logs/new_topic.html',context)

@login_required
def new_entry(request,topic_id):
    ''' 在特定的主题添加相关条目 '''
    #pylint: disable=no-member
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        #未提交数据，创建一个空表单
        form = EntryForm()
    else:
        #POST提交的数据，对数据进行处理
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse('learning_logs:topic',args=[topic_id]))
    context = {'topic':topic,'form':form}
    return render(request,'learning_logs/new_entry.html',context)

@login_required
def edit_entry(request,entry_id):
    '''编辑已有条目'''
    #pylint: disable=no-member
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    #确认申请编辑的用户是此主题所属的用户
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        #初次请求，使用当前内容填充表单
        form = EntryForm(instance=entry)
    else:
        #post提交的数据，对数据进行处理
        form = EntryForm(instance=entry,data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learning_logs:topic',args=[topic.id]))
    context = {'entry':entry,'topic':topic,'form':form}
    return render(request,'learning_logs/edit_entry.html',context)