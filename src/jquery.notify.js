/*
 * Notify v0.1 plugin for jQuery.
 *
 * Displays Desktop Notifications in supported browsers, and animated 'toast' notifications in other browsers.
 *
 * Copyright (c) 2011 Jonathan Cardy
 * Licensed under the MIT licenses.
 */

/* JSLint options  */
/* global clearTimeout, document, jQuery, setTimeout, window */
/* jslint browser: true, confusion: true, vars: true, white: true, nomen: true, plusplus: true, maxerr: 50, indent: 4 */

(function($){

	"use strict";

	//Static count of the number of notifications currently being shown.
	var count = 0;
	
	//Notification ID
	var id = 0;
	
	//Handles the (n) part being shown in the title.
	var titleManager = (function() {
		var plainTitle = document.title,
			updatedTitle = document.title;
		
		return {
			update: function(n) {
				//Ensure the current title is the updated title.
				if (document.title !== updatedTitle) {
					//It isn't - so some other script has updated the title, sync it.
					plainTitle = document.title;
				}
				
				if(n) {
					updatedTitle = "(" + n + ") " + plainTitle; //Update (n) in title
				} else {
					updatedTitle = plainTitle; //Revert to original title
				}
				
				document.title = updatedTitle;
			}
		};
	}());

	var WebkitNotification = function(timeout, onClose, onClick){ this.timeout = timeout; this._onClose = onClose; this._onClick = onClick; };
	
	WebkitNotification.prototype = {
		_getPermission: function _getPermission(callback){
			if(window.webkitNotifications.checkPermission() > 0){
				window.webkitNotifications.requestPermission(callback);
			} else {
				callback();
			}
		},
		
		_setupNotification: function _setupNotification(notification) {
			var me = this;
			this._notification = notification;
			notification.show();
			
			notification.onclose = function onClose() { me.hide();};
			notification.onclick = me._onClick;
			
			if(this.timeout) {
				this._hideTimeout = setTimeout(function hideTimeout() { me.hide(); }, this.timeout);
			}
		},
		
		hide: function hide(){
			if(this._cancelled) {
				return; //hide() is called twice on timeout - first when we call hide(), then when the notification raises onclose.
			}
			
			this._cancelled = true;
			if(this._hideTimeout) {
				clearTimeout(this._hideTimeout);
			}
			this._notification.cancel();
			this._onClose();
		},
		
		show: function show(icon, title, message){
			var me = this;
			this._getPermission(function() {
				try {
					me._setupNotification(window.webkitNotifications.createNotification(icon, title, message));
				} catch(e) { }
			});
		},
		
		showUrl: function showUrl(url) {
			var me = this;
			this._getPermission(function() {
				try {
					me._setupNotification(window.webkitNotifications.createHTMLNotification(url));
				} catch(e) { }
			});
		}
	};
	
	var fallbackNotificationQueue = (function() {
		var queue = [],
			totalHeight = 0,
			padding = 10;
		
		return {
			add: function(item) {
				queue.push(item);
				totalHeight += padding;
				
				item.element.appendTo(document.body);
				item.height = item.element.height();
				
				//Start item below the bottom of the screen and animate to its target position.
				item.element.css("bottom", -item.height + "px");
				item.element.animate({ "bottom": totalHeight }, 'fast');
				
				totalHeight += item.height;
			},
			
			remove: function remove(item) {
				var i, j,
					displaced = item.height + padding;
				
				totalHeight -= displaced;
				
				//Remove it from the queue
				i = $.inArray(item, queue);
				item.element.remove();
				queue.splice(i, 1);
				
				//Elements under it should slide down
				for(j=i; j<queue.length; j++) {
					queue[j].element.animate({ "bottom": '-=' + displaced });
				}	
			}
		};
	}());
	
	var FallbackNotification = function(timeout, onClose, onClick) { this.timeout = timeout; this._onClose = onClose; this._onClick = onClick; };
	
	FallbackNotification.prototype = {
		
		_setupNotification: function _setupNotification() {
			var me = this;
			
			$(".notification-close", this.element).click(function(){ me.hide(); });
			$(".notification-content", this.element).click(me._onClick);
			
			$("iframe", this.element).load(function() {
				$(this).contents().click(me._onClick);
			});
			
			fallbackNotificationQueue.add(this);
			
			//Only hide if the timeout is >0.
			if(this.timeout) {
				this._hideTimeout = setTimeout(function(){ me.hide(); }, this.timeout);
			}
		},
		
		hide: function hide(){
			if(this._hideTimeout) {
				clearTimeout(this._hideTimeout);
			}
			fallbackNotificationQueue.remove(this);
			this._onClose();
		},
		
		show: function show(icon, title, message) {
			this.element = $("<div class='notification-outer'><div class='notification-header'><div class='notification-title'>"+ title +"</div><div class='notification-close' title='Dismiss'></div></div><div class='notification-content'><div class='notification-icon' style='display:none;'></div><div class='notification-text'><div class='notification-body'>"+ message +"</div></div></div></div>");
			
			if (icon) {
				$(".notification-icon", this.element).show().css("background-image", "url("+ icon +")");
			}
			
			this._setupNotification();
		},
		
		showUrl: function show(url) {
			this.element = $("<div class='notification-outer'><div class='notification-close' title='Dismiss'></div><iframe src='"+ url +"'></iframe></div>");
			this._setupNotification();
		}
	};

	$.notify = function(userOptions) {
		var notification,
			currentId = ++id;
			
		//Define default options
		var options = {
			'icon': '',
			'title': 'Notification',
			'message': '',
			'url': '',
			'useFallback': !window.webkitNotifications,
			'timeout': 0,
			'showCountInTitle': !window.webkitNotifications,
			'onClose': function(){},
			'onClick': function(){},
			'closeOnClick': true,
			'obj': null
		};

		//The argument can be a string (the message) or an object of options.
		if (typeof userOptions === "string") {
			userOptions = { message: userOptions };
		} else if (!userOptions) {
			throw new Error("You need to pass an object specifying some options.");
		}
		userOptions = userOptions || {};
		$.extend(options, userOptions);
		
		var onClose = function onClose() {
			//Raise the callback
			options.onClose(currentId, options.obj);
			//Update the count
			count--;
			if (options.showCountInTitle) {
				titleManager.update(count);
			}
		};
		
		var onClick = function onClick() {
			options.onClick(currentId, options.obj);
			if (options.closeOnClick){
				notification.hide();
			}
		};
		
		var NotificationCtor = options.useFallback ? FallbackNotification : WebkitNotification;
		notification = new NotificationCtor(options.timeout, onClose, onClick);
		
		if(options.url) {
			notification.showUrl(options.url);
		} else {
			notification.show(options.icon, options.title, options.message);
		}
		
		//Update the number of notifications.
		count++;
		
		//Update the count in the title
		if	(options.showCountInTitle) {
			titleManager.update(count);
		}
		
		return id;
	};
}( jQuery ));