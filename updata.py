import requests
import os
import datetime
from dateutil import tz

token = ''
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
top_repo_num = 10
recent_repo_num = 10

from_zone = tz.tzutc()
to_zone = tz.tzlocal()


def fetcher(username: str):
    result = {
        'name': '',
        'public_repos': 0,
        'top_repos': [],
        'recent_repos': []
    }
    user_info_url = "https://api.github.com/users/{}".format(username)
    header = {} if token == "" else {"Authorization": "bearer {}".format(token)}
    res = requests.get(user_info_url, header)
    user = res.json()
    print(user)
    result['name'] = user['name']
    repos = []
    for i in range(1, 2 + user['public_repos'] // 100):
        all_repos_url = "https://api.github.com/users/{}/repos?per_page=100&page={}".format(username, i)
        res = requests.get(all_repos_url, header)
        repos.extend(res.json())
    processed_repos = []
    for repo in repos:
        if repo['fork']:
            continue
        processed_repo = {
            'score': repo['stargazers_count'] + repo['watchers_count'] + repo['forks_count'],
            'star': repo['stargazers_count'],
            'link': repo['html_url'],
            'created_at': repo['created_at'],
            'updated_at': repo['updated_at'],
            'pushed_at': repo['pushed_at'],
            'name': repo['name'],
            'description': repo['description']
        }
        date = datetime.datetime.strptime(processed_repo['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")
        date = date.replace(tzinfo=from_zone)
        date = date.astimezone(to_zone)
        processed_repo['pushed_at'] = date.strftime('%Y-%m-%d %H:%M:%S')
        processed_repos.append(processed_repo)
    top_repos = sorted(processed_repos, key=lambda x: x['star'], reverse=True)
    top_repos = top_repos[:top_repo_num]
    result['top_repos'] = top_repos
    recent_repos = sorted(processed_repos, key=lambda x: x['pushed_at'], reverse=True)
    recent_repos = recent_repos[:recent_repo_num]
    result['recent_repos'] = recent_repos
    return result

abstract_tpl = """## Abstract
<p>
  <img src="https://github-readme-stats-gray-kappa.vercel.app/api?username=nb-sb&count_private=true&show_icons=true" alt="戏人看戏's Github Stats"  width="400px" height="170px"/>
  <img src="https://stats.justsong.cn/api/leetcode/?username=nbsb&cn=true" alt="戏人看戏's LeetCode Stats" height="170px" />
</p>

<a href="#">
<div>
  <span >
    <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=nb-sb&layout=compact&hide_border=true&langs_count=10" alt="戏人看戏's Top Langs"  height="170px"  /> 
  </span>
</div>
<p>
  <img src="https://skillicons.dev/icons?i=c,cpp,go,py,html,css,js,nodejs,java,md,pytorch,tensorflow,flask,fastapi,express,qt,react,cmake,docker,git,linux,nginx,mysql,redis,sqlite,githubactions,heroku,vercel,visualstudio,vscode" alt="戏人看戏's LeetCode Stats"  />
</p>
</a>

## Make friends 👬🏻

<img src="https://media.giphy.com/media/LnQjpWaON8nhr21vNW/giphy.gif" width="60" > <em><b>I love to make friends.</b> so if you want to say <b>hi, I'll be happy to meet you more!</b> 😊</em>

"""

recent_repos_tpl = """\n## Recent Updates
|Project|Description|Last Update|
|:--|:--|:--|
"""

top_repos_tpl = """\n## Top Projects
|Project|Description|Stars|
|:--|:--|:--|
""".format(current_time)

footer_tpl = f"""
\n
*Last updated on: {current_time}*
"""


def render(github_username, github_data, zhihu_username='') -> str:
    markdown = ""
    global abstract_tpl
    if zhihu_username:
        abstract_tpl += zhihu_tpl
    markdown += abstract_tpl.format(github_username=github_username, github_name=github_data['name'],
                                    zhihu_username=zhihu_username)
    global top_repos_tpl
    for repo in github_data['top_repos']:
        top_repos_tpl += "|[{name}]({link})|{description}|`{star}⭐`|\n".format(**repo)
    markdown += top_repos_tpl
    global recent_repos_tpl
    for repo in github_data['recent_repos']:
        repo['date'] = repo['pushed_at'].replace('-', '--').replace(' ', '-').replace(':', '%3A')
        recent_repos_tpl += "|[{name}]({link})|{description}|![{pushed_at}](https://img.shields.io/badge/{date}-brightgreen?style=flat-square)|\n".format(**repo)
    markdown += recent_repos_tpl
    markdown += footer_tpl
    return markdown


def writer(markdown) -> bool:
    ok = True
    try:
        with open('./README.md', 'w',encoding='utf-8') as f:
            f.write(markdown)
    except IOError:
        ok = False
        print('unable to write to file')
    return ok


def pusher():
    commit_message = ":pencil2: update on {}".format(current_time)
    os.system('git add ./README.md')
    if os.getenv('DEBUG'):
        return
    os.system('git commit -m "{}"'.format(commit_message))
    os.system('git push')


def main():
    global top_repo_num
    global recent_repo_num
    top_repo_num = 10
    recent_repo_num = 10
    github_username = "nb-sb"
    if not github_username:
        cwd = os.getcwd()
        github_username = os.path.split(cwd)[-1]
    # zhihu_username = os.getenv('ZHIHU_USERNAME')
    github_data = fetcher(github_username)
    markdown = render(github_username, github_data, '')
    if writer(markdown):
        pass
        # pusher()


if __name__ == '__main__':
    main()
