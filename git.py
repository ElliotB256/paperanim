# -*- coding: utf-8 -*-
import subprocess
import os
import ghostscript
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import time

ffmpeg = 'C:/Users/bentine/Downloads/ffmpeg-20200528-c0f01ea-win64-static/bin/ffmpeg.exe'

def get_commits():
    """Returns a list of all git commit hashes in the current working directory."""
    commits = []
    p = subprocess.Popen("git log --pretty=\"%h\"", shell=True, stdout=subprocess.PIPE)
    for line in p.stdout.readlines():
        commits.append(line.decode('utf-8').strip())
    return commits

def checkout(commit):
    """Performs git checkout in the current working directory to the stated commit hash or branch."""
    subprocess.run("git checkout -f {}".format(commit))

def latex(file):
    """Invokes pdflatex to build the given tex file."""
    p = subprocess.Popen("pdflatex.exe {}".format(file), shell=True, stdout=subprocess.PIPE)
    # Note: sometimes pdflatex will pause and wait for input. Bit of a hack to just give it a return.
    p.communicate(input='\n')

def render_pdf(pdf_file, image_directory):
    """Uses ghostscript to render each page of the pdf file as images in the image_directory."""
    jpeg_output_path = image_directory + 'main_p%03d.jpg'
    ghostscript.Ghostscript(b"pdf2jpeg",
            b"-dNOPAUSE",
            b"-sDEVICE=jpeg",
            b"-r300",
            ("-sOutputFile=" + jpeg_output_path).encode('utf-8'),
            pdf_file.encode('utf-8')
            )
    
def plot_pages(image_dir, composite_image_file):
    """Loads page images from the image directory, plots a composite image, and saves it to the composite_image_file."""
    dpi=96
    plt.figure(figsize=(1920/dpi, 1080/dpi), dpi=dpi)
    flat = []

    # Create the axes used for each page.    
    for row in np.arange(0,3):
        for col in np.arange(0, 5):        
            h = 1.0/3;
            w = 0.2;
            ax = plt.axes([col*w, 1-(row+1)*h, w, h], aspect=(h/w))
            flat.append(
                   ax
                    )
    
    # Plot each page
    for i in np.arange(0,15):
        page_file = "main_p{:03d}.jpg".format(i+1)
        image_path = image_dir + page_file
        plot_image(flat[i], image_path)
    plt.savefig(composite_image_file, dpi=dpi)
    plt.show()
    
    
def plot_image(axes, image_path):
    """Plot the image in the image_path to the given axes"""
    try:
        with Image.open(image_path) as img:
            axes.imshow(img)
    except:
        pass
    axes.spines['top'].set_visible(False)
    axes.spines['left'].set_visible(False)
    axes.spines['bottom'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.set_xticks([])
    axes.set_yticks([])
    
def render_commits(path, image_dir):
    """Render each commit in the git repository on path to the image_dir directory."""
    os.chdir(path)
    commits = get_commits()
    print("Found {} commits.".format(len(commits)))
    n = len(commits)
    for i in np.arange(0,n):
        try:
            commit = commits[i]
            print("Rendering commit {} ({} of {})...".format(commit, i, n))
            checkout(commit)
            time.sleep(0.02)
            latex('main.tex')
            time.sleep(0.02)
            if os.path.exists(image_dir):
                for root, dirs, files in os.walk(image_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(image_dir)
            os.mkdir(image_dir)
            time.sleep(0.02)
            render_pdf('main.pdf', image_dir)
            time.sleep(0.02)
            plot_pages(image_dir, 'C:/code/paperanim/output/{}.png'.format(commit))
        except:
            print("Error.")
    checkout('master')
    
def combine_to_video(repo_path, output_path, video_path):
    """Combine the rendered commit images into a video using ffmpeg."""
    os.chdir(repo_path)
    commits = get_commits()
    commits.reverse()
    print("Found {} commits.".format(len(commits)))
    n = len(commits)
    counter = 0
    fps = 3
    end_delay = 5
    for i in np.arange(0,n+end_delay*fps):
        j = min(i, len(commits)-1)
        commit = commits[j]
        image_path = ('{}.png'.format(commit))
        print('commit: {} at path={}'.format(commit, image_path))
        try:
            cmd = 'copy {} {}'.format(image_path, video_path+'{:03d}.png'.format(counter)).replace('/', '\\')
            print(cmd)
            os.chdir(output_path)
            subprocess.check_output(cmd, shell=True)
            counter = counter + 1
        except:
            print('cant copy image - image not found?')
            # Ideally I would do this using file exists, but at least on windows I found the behaviour was inconsistent.
            # Copy and handling the exception seems to work more reliably.
            
    os.chdir(video_path)
    cmd = '{} -f image2 -r {} -i %03d.png -vcodec mpeg4 -y paper.mp4'.format(
                ffmpeg,
                fps
                )
    print(cmd)
    subprocess.run(cmd)
    print('finished!')    
    
if __name__ == "__main__":
    render_commits("C:/code/inelasticpaperCopy", "C:/code/inelasticpaperCopy/render/")
    combine_to_video(
            'C:/Code/inelasticpaperCopy',
            'C:/Code/paperanim/output/',
            'C:/Code/paperanim/video/'
            )
    